from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError
from rest_framework.authtoken.models import Token


User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=8, write_only=True, style={"input_type": "password"}
    )

    confirm_password = serializers.CharField(
        min_length=8, write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["email", "username", "password", "confirm_password"]

    def validate(self, attrs):
        email_exist = User.objects.filter(email=attrs["email"]).exists()

        if email_exist:
            raise ValidationError("Email already in use")
        elif attrs["password"] != attrs["confirm_password"]:
            raise ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user
