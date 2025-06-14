from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from ingredients.models import Ingredient

# Константы для избегания "magic numbers"
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000
MIN_AMOUNT = 1
MAX_AMOUNT = 32000


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes", verbose_name="Автор"
    )
    name = models.CharField(max_length=200, verbose_name="Название", db_index=True)
    image = models.ImageField(upload_to="recipes/", verbose_name="Картинка")
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", verbose_name="Ингредиенты"
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f"Минимальное время приготовления {MIN_COOKING_TIME} минута",
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=f"Максимальное время приготовления {MAX_COOKING_TIME} минут",
            ),
        ],
        verbose_name="Время приготовления (мин)",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент"
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_AMOUNT, message=f"Минимальное количество ингредиента {MIN_AMOUNT}"
            ),
            MaxValueValidator(
                MAX_AMOUNT, message=f"Максимальное количество ингредиента {MAX_AMOUNT}"
            ),
        ],
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        ordering = ["recipe", "ingredient"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique_recipe_ingredient"
            )
        ]

    def __str__(self):
        return f"{self.ingredient} в {self.recipe}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], name="unique_favorite")
        ]

    def __str__(self):
        return f"{self.user} добавил {self.recipe} в избранное"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart_items",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="shopping_cart",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            )
        ]

    def __str__(self):
        return f"{self.user} добавил {self.recipe} в список покупок"
