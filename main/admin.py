from django.contrib import admin
from .models import Category, Store, Product, Price, UserProfile, Favorite


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'color', 'created_at')
    prepopulated_fields = {'slug': ('name',)}


class PriceInline(admin.TabularInline):
    model = Price
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'min_price', 'store_count')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'description', 'brand')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PriceInline]


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'store', 'price', 'old_price', 'is_available', 'updated_at')
    list_filter = ('store', 'is_available')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
