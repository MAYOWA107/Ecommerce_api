from rest_framework import serializers
from .models import Product, Category, Cart, CartItem, Review, WishList
from django.contrib.auth import get_user_model


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "slug", "image"]


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "category", "slug", "image"]


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image", "products"]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField(method_name="get_sub_total")

    class Meta:
        model = CartItem
        fields = ["id", "cart", "product", "quantity", "sub_total"]

    def get_sub_total(self, cartitem):
        total = cartitem.product.price * cartitem.quantity
        return total


class CartSerializer(serializers.ModelSerializer):
    cartitems = CartItemSerializer(read_only=True, many=True)
    cart_total = serializers.SerializerMethodField(method_name="get_cart_total")

    class Meta:
        model = Cart
        fields = ["id", "cart_code", "cartitems", "cart_total"]

    def get_cart_total(self, cart):
        items = cart.cartitems.all()
        total = sum([item.quantity * item.product.price for item in items])
        return total


class CartStatSerializer(serializers.ModelSerializer):
    total_quantity = serializers.SerializerMethodField(method_name="get_total_quantity")

    class Meta:
        model = Cart
        fields = ["id", "cart_code", "total_quantity"]

        def get_total_quantity(self, cart):
            items = cart.cartitems.all()
            total_quantity = 0
            for item in items:
                total_quantity += item.quantity
            return total_quantity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "first_name", "last_name", "profile_pic_url"]


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "review", "created_at", "updated_at"]


class WishlistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = WishList
        fields = ["id", "created_at", "user", "product", "created_at"]
