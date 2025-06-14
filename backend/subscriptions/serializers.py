from rest_framework import serializers
from users.models import User, Subscription
from recipes.serializers import RecipeShortSerializer


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(user=request.user, subscriber=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes = obj.recipes.all()

        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit:
            try:
                recipes = recipes[: int(recipes_limit)]
            except (ValueError, TypeError):
                pass

        return RecipeShortSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_avatar(self, obj):
        if obj.avatar and hasattr(obj.avatar, "url"):
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
