from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=254, unique=True, verbose_name="Электронная почта"
    )
    username = models.CharField(
        max_length=150, unique=True, verbose_name="Имя пользователя"
    )
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    description = models.TextField(blank=True, verbose_name="О себе")
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribers", verbose_name="Автор"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subscriber"], name="unique_subscription"
            ),
            models.CheckConstraint(
                check=~models.Q(user_id=models.F("subscriber_id")),
                name="no_self_subscription",
            ),
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.subscriber}"
