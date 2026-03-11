from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Product,
    Category,
    Review,
    WishList,
)
from django.contrib.auth import get_user_model
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    CategoryDetailSerializer,
    CategoryListSerializer,
    ReviewSerializer,
    WishlistSerializer,
)
from rest_framework.response import Response
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe

endpoint_secret = settings.WEBHOOK_SECRET
User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(["GET"])
@permission_classes([AllowAny])
def product_list(request):
    products = Product.objects.filter(featured=True)
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    serializer = ProductDetailSerializer(product)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategoryListSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes(AllowAny)
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    serializer = CategoryDetailSerializer(category)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    cart_code = request.data.get("cart_code")
    product_id = request.data.get("product_id")
    cart, created = Cart.objects.get_or_create(cart_code=cart_code)
    product = Product.objects.get(id=product_id)

    cartitem, created = CartItem.objects.get_or_create(product=product, cart=cart)
    cartitem.quantity = 1
    cartitem.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cartitem_delete(request, pk):
    cartitem = get_object_or_404(CartItem, id=pk)
    cartitem.delete()
    return Response("cartitem has been deleted successfully.", status=204)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get("item_id")
    quantity = request.data.get("quantity")
    quantity = int(quantity)

    cartitem = get_object_or_404(CartItem, id=cartitem_id)
    cartitem.quantity = quantity
    cartitem.save()

    serializer = CartItemSerializer(cartitem)
    return Response(
        {"data": serializer.data, "message": "cartitem updated succesfully"}
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_review(request):
    product_slug = request.data.get("product_slug")
    rating = request.data.get("rating")
    review_text = request.data.get("review")

    product = get_object_or_404(Product, slug=product_slug)
    user = request.user

    # if user.username != request.username:
    #   return Response(
    #      {"error": "You are not allowed to update this review"}, status=403
    # )

    if Review.objects.filter(product=product, user=user).exists():
        return Response(
            {"error": "You have already reviewed this product."}, status=400
        )

    review = Review.objects.create(
        product=product, user=user, rating=rating, review=review_text
    )
    serializer = ReviewSerializer(review)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_review(request, pk):
    review = get_object_or_404(Review, id=pk)
    rating = request.data.get("rating")
    review_text = request.data.get("review_text")

    if review.user != request.user:
        return Response(
            {"error": "You are not allowed to update this review"}, status=403
        )

    review.rating = rating
    review.review = review_text
    review.save()

    serializer = ReviewSerializer(review)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    review = get_object_or_404(Review, id=pk)

    # if review.user != request.user:
    #   return Response(
    #      {"error": "You are not allowed to delete this review"}, status=403
    # )

    review.delete()

    return Response("Review has been deleted successfully.", status=204)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def add_wishlist(request):
    if request.method == "POST":
        product_id = request.data.get("product_id")

        product = Product.objects.get(id=product_id)
        user = request.user
        wishlist = WishList.objects.filter(user=user, product=product)

        if wishlist:
            wishlist.delete()
            return Response("Wishlist has been deleted successfully.", status=204)

        new_wishlist = WishList.objects.create(product=product, user=user)
        new_wishlist.save()

        serializer = WishlistSerializer(new_wishlist)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def search_product(request):
    query = request.query_params.get("search")

    if not query:
        return Response("No query provided.", status=400)
    product = Product.objects.filter(
        Q(name__icontains=query)
        | Q(description__icontains=query)
        | Q(category__name__icontains=query)
    )
    serializer = ProductListSerializer(product, many=True)
    return Response(serializer.data)


# Stripe implementation for payment


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    cart_code = request.data.get("cart_code")
    email = request.data.get("email")
    cart = Cart.objects.get(
        cart_code=cart_code,
    )
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": item.product.name},
                        "unit_amount": int(item.product.price) * 100,
                    },
                    "quantity": item.quantity,
                }
                for item in cart.cartitems.all()
            ],
            mode="payment",
            success_url="https://webflow.com/made-in-webflow/website/successful-payment",
            cancel_url="http://localhost:3000/cancel",
            metadata={"cart_code": cart_code},
        )
        return Response({"data": checkout_session})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if (
        event["type"] == "checkout.session.completed"
        or event["type"] == "checkout.session.async_payment_succeeded"
    ):
        session = event["data"]["object"]
        cart_code = session.get("metadata", {}).get("cart_code")
        fulfill_checkout(session, cart_code)
    return HttpResponse(status=200)


def fulfill_checkout(session, cart_code):
    order = Order.objects.create(
        stripe_checkout_id=session["id"],
        amount=session["amount_total"],
        currency=session["currency"],
        customer_email=session["customer_email"],
        status="Paid",
    )

    cart = Cart.objects.get(cart_code=cart_code)
    cartitems = cart.cartitems.all()
    for item in cartitems:
        orderitem = OrderItem.objects.create(
            order=order, product=item.product, quantity=item.quantity
        )

    cart.delete()
