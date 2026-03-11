from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="category_image", null=True, blank=True)

    class Meta:
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Category.objects.filter(slug=self.slug).exists():
                unique_slug = f"{self.slug}- {counter}"
                counter += 1
            self.slug = unique_slug
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(unique=True, blank=True)
    featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to="product_image", null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="products",
    )

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{self.slug}-{counter}"
                counter += 1
            self.slug = unique_slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# adding Cart models
class Cart(models.Model):
    cart_code = models.CharField(max_length=11, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cart_code


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cartitems")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items")
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart {self.cart.cart_code}"


class Review(models.Model):
    Rating_Choices = [
        (1, "1 = Poor"),
        (2, "2 = Fair"),
        (3, "3 = Good"),
        (4, "4 = Very Good"),
        (5, "5 = Excellent"),
    ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveIntegerField(choices=Rating_Choices, default=1)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s review on {self.product.name}."

    class Meta:
        unique_together = ["user", "product"]
        ordering = ["-created_at"]


class ProductRating(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="rating"
    )
    average_rating = models.FloatField(default=0.0)
    total_review = models.PositiveIntegerField(default=0)

    def __str__(self):
        return (
            f"{self.product.name} - {self.average_rating} - {self.total_review} reviews"
        )


class WishList(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlist"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlists"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "product"]

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"


class Order(models.Model):
    status_choices = (
        ("Pending", "PENDING"),
        ("Paid", "PAID"),
    )
    stripe_checkout_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    customer_email = models.EmailField()
    status = models.CharField(max_length=20, choices=status_choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.stripe_checkout_id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="orderitems"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Order {self.product.name} - {self.order.stripe_checkout_id}"
