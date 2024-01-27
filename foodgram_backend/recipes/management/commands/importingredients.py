from django.core.management.base import BaseCommand
import csv
from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Ипортирование ингредиентов из файла CSV.'

    def handle(self, *args, **kwargs):
        with open('recipes/data/ingredients.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)

            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
                self.stdout.write(self.style.SUCCESS(f'Imported: {name}'))
