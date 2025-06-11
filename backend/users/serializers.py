import base64
import uuid
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from .models import User, Subscription
from recipes.serializers import RecipeShortSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # Извлекаем формат и данные Base64
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]  # Например, 'png' или 'jpg'
            # Декодируем Base64
            decoded_file = base64.b64decode(imgstr)
            # Генерируем уникальное имя файла
            file_name = f"{uuid.uuid4()}.{ext}"
            # Создаём ContentFile для сохранения
            data = ContentFile(decoded_file, name=file_name)
        return super().to_internal_value(data)


class CustomUserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, subscriber=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='subscriber.email')
    id = serializers.ReadOnlyField(source='subscriber.id')
    username = serializers.ReadOnlyField(source='subscriber.username')
    first_name = serializers.ReadOnlyField(source='subscriber.first_name')
    last_name = serializers.ReadOnlyField(source='subscriber.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        from recipes.models import Recipe
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit', 3)
        recipes = Recipe.objects.filter(author=obj.subscriber)[:int(recipes_limit)]
        serializer = RecipeShortSerializer(recipes, many=True, context={'request': request})
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.subscriber.recipes.count()