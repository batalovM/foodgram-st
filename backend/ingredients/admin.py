from django.contrib import admin
from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    list_filter = ("measurement_unit",)
    search_fields = ("name",)
    ordering = ("name",)
    empty_value_display = "-пусто-"
