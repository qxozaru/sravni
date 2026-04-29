from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Min, Max, Count
from django.http import JsonResponse
from django.utils.text import slugify
from unidecode import unidecode

from .models import Product, Store, Category, Price, UserProfile, Favorite
from .forms import RegisterForm, UserProfileForm, ProductForm, PriceForm


def _slug(name):
    try:
        return slugify(unidecode(name))
    except Exception:
        return slugify(name) or name.lower().replace(' ', '-')


def index(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    popular = Product.objects.filter(
        prices__is_available=True
    ).annotate(
        fav_count=Count('favorited_by'),
        lowest=Min('prices__price'),
    ).order_by('-fav_count', '-created_at').distinct()[:12]

    discounted = Price.objects.filter(
        old_price__isnull=False, old_price__gt=0, is_available=True
    ).select_related('product', 'store').order_by('price')[:8]

    stores = Store.objects.annotate(
        product_count=Count('prices', filter=Q(prices__is_available=True))
    )

    return render(request, 'main/index.html', {
        'categories': categories,
        'popular_products': popular,
        'discounted_prices': discounted,
        'stores': stores,
        'total_products': Product.objects.count(),
        'total_stores': Store.objects.count(),
    })


def product_list(request):
    products = Product.objects.all()
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('category', '')
    sort = request.GET.get('sort', 'popular')
    brand = request.GET.get('brand', '')
    available = request.GET.get('available', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')

    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(brand__icontains=q))
    if cat:
        products = products.filter(category__slug=cat)
    if brand:
        products = products.filter(brand__iexact=brand)
    if available == 'yes':
        products = products.filter(prices__is_available=True).distinct()

    products = products.annotate(
        min_p=Min('prices__price'),
        max_p=Max('prices__price'),
        shop_count=Count('prices', filter=Q(prices__is_available=True)),
    )

    if price_min:
        try:
            products = products.filter(min_p__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(min_p__lte=float(price_max))
        except ValueError:
            pass

    sort_map = {
        'price_asc': 'min_p',
        'price_desc': '-min_p',
        'new': '-created_at',
        'name': 'name',
        'popular': '-shop_count',
    }
    products = products.order_by(sort_map.get(sort, '-shop_count'))

    categories = Category.objects.all()
    brands = Product.objects.values_list('brand', flat=True).distinct().order_by('brand')
    brands = [b for b in brands if b]

    return render(request, 'main/product_list.html', {
        'products': products,
        'categories': categories,
        'brands': brands,
        'query': q,
        'current_category': cat,
        'current_sort': sort,
        'current_brand': brand,
        'current_available': available,
        'current_price_min': price_min,
        'current_price_max': price_max,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    prices = product.prices.select_related('store').order_by('price')
    is_fav = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, product=product).exists()

    # Похожие товары
    similar = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk).annotate(
        min_p=Min('prices__price')
    )[:4] if product.category else []

    return render(request, 'main/product_detail.html', {
        'product': product,
        'prices': prices,
        'is_favorite': is_fav,
        'similar': similar,
    })


def store_list(request):
    stores = Store.objects.annotate(
        product_count=Count('prices', filter=Q(prices__is_available=True))
    ).order_by('-product_count')
    return render(request, 'main/store_list.html', {'stores': stores})


def store_detail(request, slug):
    store = get_object_or_404(Store, slug=slug)
    prices = store.prices.filter(is_available=True).select_related('product', 'product__category').order_by('product__name')
    return render(request, 'main/store_detail.html', {'store': store, 'prices': prices})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Добро пожаловать в Сравни!')
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f'С возвращением, {form.get_user().username}!')
            return redirect(request.GET.get('next', 'index'))
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    return render(request, 'main/profile.html', {'form': form, 'favorites': favorites})


@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
        added = False
    else:
        added = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'added': added})
    return redirect('product_detail', slug=product.slug)


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.slug = _slug(product.name)
            base = product.slug
            n = 1
            while Product.objects.filter(slug=product.slug).exists():
                product.slug = f'{base}-{n}'
                n += 1
            product.save()
            messages.success(request, 'Товар добавлен!')
            return redirect('product_detail', slug=product.slug)
    else:
        form = ProductForm()
    return render(request, 'main/add_product.html', {'form': form})


@login_required
def add_price(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = PriceForm(request.POST)
        if form.is_valid():
            price = form.save(commit=False)
            price.product = product
            existing = Price.objects.filter(product=product, store=price.store).first()
            if existing:
                existing.price = price.price
                existing.old_price = price.old_price
                existing.is_available = price.is_available
                existing.save()
                messages.info(request, 'Цена обновлена!')
            else:
                price.save()
                messages.success(request, 'Цена добавлена!')
            return redirect('product_detail', slug=product.slug)
    else:
        form = PriceForm()
    return render(request, 'main/add_price.html', {'form': form, 'product': product})
