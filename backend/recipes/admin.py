from django.contrib import admin
from .models import Recipe, RecipeIngredient, Favorite, ShoppingCart


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "cooking_time", "created_at")
    list_filter = ("author", "created_at")
    search_fields = ("name", "author__username")
    inlines = (RecipeIngredientInline,)
    ordering = ("-created_at",)
    empty_value_display = "-пусто-"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "amount")
    list_filter = ("recipe", "ingredient")
    search_fields = ("recipe__name", "ingredient__name")
    empty_value_display = "-пусто-"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    list_filter = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    empty_value_display = "-пусто-"


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    list_filter = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    empty_value_display = "-пусто-"
