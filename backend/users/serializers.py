from rest_framework import serializers
from .models import User, Subscription


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
        return True  # Все пользователи в подписках уже подписаны

    def get_recipes(self, obj):
        from recipes.models import Recipe  # Ленивый импорт
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit', 3)
        recipes = Recipe.objects.filter(author=obj.subscriber)[:int(recipes_limit)]
        serializer = serializers.ModelSerializer(
            recipes,
            fields=('id', 'name', 'cooking_time'),
            many=True,
            context={'request': request}
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.subscriber.recipes.count()