import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'import data from csv'

    def handle(self, *args, **options):
        with open('data/ingredients.csv', 'r', encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for row in reader:
                name, unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=unit,
                )
    print('Импорт выполнен')
