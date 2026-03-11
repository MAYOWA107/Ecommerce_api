from django.urls import path
from .views import (
    product_list,
    product_detail,
    category_list,
    category_detail,
    add_to_cart,
    update_cartitem_quantity,
    add_review,
    update_review,
    delete_review,
    add_wishlist,
    cartitem_delete,
    search_product,
    create_checkout_session,
    my_webhook_view,
)


urlpatterns = [
    path("products", product_list, name="products"),
    path("product/<slug:slug>", product_detail, name="products"),
    path("categories", category_list, name="categories"),
    path("category/<slug:slug>", category_detail, name="category"),
    path("add_to_cart/", add_to_cart, name="add_to_cart"),
    path("cartitem_delete/<int:pk>", cartitem_delete, name="cartitem_delete"),
    path("update_quantity", update_cartitem_quantity, name="update_quantity"),
    path("add_review", add_review, name="add_review"),
    path("update_review/<int:pk>", update_review, name="update_review"),
    path("delete_review/<int:pk>", delete_review, name="delete_review"),
    path("add_wishlist", add_wishlist, name="add_wishlist"),
    path("search_product", search_product, name="search_product"),
    path("payment", create_checkout_session, name="payment"),
    path("webhook", my_webhook_view, name="webhook"),
]
