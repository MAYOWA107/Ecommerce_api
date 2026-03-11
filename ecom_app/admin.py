from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    Product,
    Category,
    Review,
    ProductRating,
    WishList,
    Order,
    OrderItem,
)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "featured")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register([Cart, CartItem, Review, ProductRating, WishList, Order, OrderItem])
