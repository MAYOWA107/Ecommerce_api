from django.urls import path
from .views import SignupView, LoginView, change_password


urlpatterns = [
    path("signup", SignupView.as_view(), name="signup"),
    path("login", LoginView.as_view(), name="login"),
    path("change_password", change_password, name="password_change"),
]
