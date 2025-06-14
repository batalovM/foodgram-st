import random
import io
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from recipes.models import Recipe, RecipeIngredient
from ingredients.models import Ingredient
from PIL import Image

User = get_user_model()


class Command(BaseCommand):
    help = "Создает тестовых пользователей и рецепты"

    def handle(self, *args, **kwargs):
        if Recipe.objects.filter(author__username__startswith="test_user").exists():
            self.stdout.write(
                self.style.WARNING(
                    "Тестовые данные уже существуют. Пропускаем создание."
                )
            )
            return

        self.stdout.write("Создание тестовых пользователей...")

        users = []
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                username=f"user{i}",
                defaults={
                    "email": f"test{i}@example.com",
                    "first_name": f"имя{i}",
                    "last_name": f"фамилия{i}",
                },
            )
            if created:
                user.set_password("password123")
                user.save()
                self.stdout.write(f"Создан пользователь {user.username}")
            users.append(user)

        ingredients = list(Ingredient.objects.all())
        if not ingredients:
            self.stdout.write(
                self.style.ERROR("Не найдены ингредиенты в базе. Сначала загрузите их.")
            )
            return

        self.stdout.write("Создание тестовых рецептов...")

        recipe_templates = [
            {
                "name": "Омлет с помидорами",
                "text": "Взбейте яйца, добавьте соль и перец. Нарежьте помидоры кубиками. Обжарьте на сковороде, залейте яйцами и готовьте до золотистой корочки.",
                "cooking_time": 15,
                "color": (255, 200, 100),  # Цвет для генерации изображения
            },
            {
                "name": 'Салат "Цезарь"',
                "text": "Нарежьте салат, курицу и помидоры. Добавьте сухарики и заправьте специальным соусом.",
                "cooking_time": 20,
                "color": (100, 200, 100),
            },
            {
                "name": "Паста карбонара",
                "text": "Отварите макароны. Обжарьте бекон, смешайте с яйцом и сыром. Добавьте к макаронам и перемешайте.",
                "cooking_time": 25,
                "color": (220, 180, 140),
            },
            {
                "name": "Тирамису",
                "text": "Смешайте маскарпоне с яйцами и сахаром. Пропитайте печенье кофе и ликером. Выложите слоями в форму.",
                "cooking_time": 240,
                "color": (160, 120, 90),
            },
            {
                "name": "Овощное рагу",
                "text": "Нарежьте овощи, обжарьте на оливковом масле, добавьте специи и томите до готовности.",
                "cooking_time": 45,
                "color": (120, 180, 70),
            },
        ]

        def create_test_image(color):
            image = Image.new("RGB", (300, 200), color=color)
            image_io = io.BytesIO()
            image.save(image_io, format="JPEG")
            image_file = SimpleUploadedFile(
                name=f"test_image_{color[0]}_{color[1]}_{color[2]}.jpg",
                content=image_io.getvalue(),
                content_type="image/jpeg",
            )
            return image_file

        for i, user in enumerate(users):
            template = recipe_templates[i % len(recipe_templates)]

            test_image = create_test_image(template["color"])

            recipe = Recipe.objects.create(
                author=user,
                name=template["name"],
                text=template["text"],
                cooking_time=template["cooking_time"],
                image=test_image,
            )

            selected_ingredients = random.sample(
                ingredients, random.randint(3, min(6, len(ingredients)))
            )
            for ingredient in selected_ingredients:
                RecipeIngredient.objects.create(
                    recipe=recipe, ingredient=ingredient, amount=random.randint(1, 500)
                )

            self.stdout.write(
                f'Создан рецепт "{recipe.name}" для пользователя {user.username}'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Успешно создано {len(users)} тестовых пользователей и {len(users)} рецептов"
            )
        )
