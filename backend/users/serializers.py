import re
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from .models import User, Subscription
from utils.serializers import Base64ImageField
from rest_framework.exceptions import AuthenticationFailed


class CustomUserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}
    
    def validate_username(self, value):
            """Валидация поля username по регулярному выражению."""
            if not re.match(r'^[\w.@+-]+$', value):
                raise serializers.ValidationError(
                    'Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_'
                )
            return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ("avatar",)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def to_representation(self, instance):
        if instance.is_anonymous:
            raise AuthenticationFailed("Authentication credentials were not provided.")
        return super().to_representation(instance)

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return user.subscriptions.filter(subscriber=obj).exists()
