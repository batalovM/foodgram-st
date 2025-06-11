import json
from django.core.management.base import BaseCommand
from ingredients.models import Ingredient

class Command(BaseCommand):
    help = 'Загружает ингредиенты из JSON файла'

    def handle(self, *args, **kwargs):
        with open('../data/ingredients.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
        self.stdout.write(self.style.SUCCESS('Ингредиенты успешно загружены'))