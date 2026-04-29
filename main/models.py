from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    icon = models.CharField('Иконка (emoji)', max_length=10, default='📦')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Store(models.Model):
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    address = models.CharField('Адрес', max_length=500, blank=True)
    website = models.URLField('Сайт', blank=True)
    logo_url = models.URLField('URL логотипа', max_length=500, blank=True)
    color = models.CharField('Цвет бренда', max_length=7, default='#333333')
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('Название', max_length=300)
    slug = models.SlugField('URL', max_length=300, unique=True)
    description = models.TextField('Описание', blank=True)
    specs = models.TextField('Характеристики', blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products',
        verbose_name='Категория'
    )
    image_url = models.URLField('URL изображения', max_length=700, blank=True)
    brand = models.CharField('Бренд', max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def min_price(self):
        p = self.prices.filter(is_available=True).order_by('price').first()
        return p.price if p else None

    @property
    def max_price(self):
        p = self.prices.filter(is_available=True).order_by('-price').first()
        return p.price if p else None

    @property
    def best_offer(self):
        return self.prices.filter(is_available=True).select_related('store').order_by('price').first()

    @property
    def store_count(self):
        return self.prices.filter(is_available=True).count()

    @property
    def savings(self):
        mn, mx = self.min_price, self.max_price
        if mn and mx and mx > mn:
            return mx - mn
        return None


class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    old_price = models.DecimalField('Старая цена', max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField('В наличии', default=True)
    product_url = models.URLField('Ссылка на товар', max_length=500, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'
        unique_together = ('product', 'store')
        ordering = ['price']

    def __str__(self):
        return f'{self.product.name} — {self.store.name}: {self.price} ₽'

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((1 - self.price / self.old_price) * 100)
        return 0

    @property
    def is_cheapest(self):
        return self.price == self.product.min_price


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True)
    city = models.CharField('Город', max_length=100, default='Красноярск')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль {self.user.username}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('user', 'product')
