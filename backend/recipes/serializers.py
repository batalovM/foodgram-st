from rest_framework import serializers
from .models import Recipe, RecipeIngredient, Favorite, ShoppingCart
from ingredients.models import Ingredient
from users.serializers import UserSerializer
from utils.serializers import Base64ImageField


class IngredientInRecipeWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError("Ингредиент с таким ID не существует.")
        return value


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True, write_only=True)  # Только для записи
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def validate(self, data):
        ingredients = data.get('ingredients')
        cooking_time = data.get('cooking_time')

        # Проверка на пустой список ингредиентов
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Поле ingredients не может быть пустым.'
            })

        # Проверка на дублирующиеся id ингредиентов
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты не должны повторяться.'
            })

        # Проверка, что cooking_time >= 1
        if cooking_time is not None and cooking_time < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть не менее 1 минуты.'
            })

        return data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        image = validated_data.pop('image', None)
        validated_data.pop('author', None)  # Удаляем author, если он есть
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            image=image,
            **validated_data
        )
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient_data['id']),
                amount=ingredient_data['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        if ingredients_data:
            instance.recipe_ingredients.all().delete()
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=Ingredient.objects.get(id=ingredient_data['id']),
                    amount=ingredient_data['amount']
                )
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['ingredients'] = RecipeIngredientSerializer(
            instance.recipe_ingredients.all(), many=True
        ).data
        return representation