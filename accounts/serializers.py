from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, smart_str, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import send_normal_email
from .mixins import ImageUploadMixin


class UserRegisterSerializer(serializers.ModelSerializer, ImageUploadMixin):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ["email", "image", "first_name", "last_name", "password", "password2"]

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise serializers.ValidationError(_("Passwords do not match"))

        return attrs

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            password=validated_data.get("password"),
        )
        if image:
            user.image = self.upload_image(image)
            user.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "full_name",
            "access_token",
            "refresh_token",
        ]

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        request = self.context.get("request")
        user = authenticate(request, email=email, password=password)

        if not user:
            raise AuthenticationFailed("invalid credentials.")
        if not user.is_verified:
            raise AuthenticationFailed("User Email not verified.")

        user_tokens = user.tokens()

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.get_full_name,
            "access_token": str(user_tokens.get("access")),
            "refresh_token": str(user_tokens.get("refresh")),
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=6)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get("request")
            site_domain = get_current_site(request).domain
            relative_link = reverse(
                "password-reset-confirm", kwargs={"uidb64": uid64, "token": token}
            )
            abs_link = f"https://{site_domain}{relative_link}"
            message = f"Hello {user.first_name}, use the link below to reset your password\n {abs_link}"
            data = {
                "message": message,
                "subject": "Reset your password",
                "to": user.email,
            }

            send_normal_email(data)

        return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    confirm_password = serializers.CharField(
        max_length=68, min_length=6, write_only=True
    )
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        fields = ["password", "confirm_password", "uidb64", "token"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            confirm_password = attrs.get("confirm_password")
            uidb64 = attrs.get("uidb64")
            token = attrs.get("token")

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return AuthenticationFailed("reset ink is invalid", 401)

            if password != confirm_password:
                raise AuthenticationFailed("passwords did not match")

            user.set_password(password)
            user.save()

            return user
        except Exception as e:
            return AuthenticationFailed("reset ink is invalid", 401)


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "image", "first_name", "last_name"]

    def validate(self, attrs):
        return super().validate(attrs)


class ProfileUpdateSerializer(serializers.ModelSerializer, ImageUploadMixin):
    id = serializers.UUIDField(read_only=True)
    image = serializers.ImageField(required=False, write_only=True)
    first_name = serializers.CharField(max_length=255, required=False)
    last_name = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "image", "first_name", "last_name"]

    def update(self, instance, validated_data):
        image = validated_data.pop('image', None)
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        if image:
            instance.image = self.upload_image(image)
        if first_name:
            instance.first_name = validated_data.get('first_name', instance.first_name)
        if last_name:
            instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance

    def validate(self, attrs):
        return super().validate(attrs)
