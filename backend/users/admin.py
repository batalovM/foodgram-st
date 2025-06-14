from django.contrib import admin
from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name")
    list_filter = ("email", "username")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("username",)
    empty_value_display = "-пусто-"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "subscriber")
    list_filter = ("user__username", "subscriber__username")
    search_fields = ("user__username", "subscriber__username")
    empty_value_display = "-пусто-"
