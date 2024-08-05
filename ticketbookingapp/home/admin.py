
from django.contrib import admin
from django.utils.html import format_html
from .models import Movie, MovieCategory, Cart, CartItems

@admin.register(MovieCategory)
class MovieCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('movie_name', 'price', 'category', 'image_preview')
    search_fields = ('movie_name', 'category__category_name')

    def image_preview(self, obj):
        return format_html('<img src="{url}" style="width: 100px; height: auto;" />', url=obj.images)

    image_preview.short_description = 'Image Preview'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_paid')

@admin.register(CartItems)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ('cart', 'movie')


