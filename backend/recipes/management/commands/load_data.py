import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient

NAME = 0
MEASUREMENT_UNIT = 1


class Command(BaseCommand):
    help = 'Загрузка данных из .csv файлов'

    def _load_ingredient(self):
        with open(
                '../data/ingredients.csv',
                encoding='utf-8'
        ) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[NAME],
                    measurement_unit=row[MEASUREMENT_UNIT],
                )
        self.stdout.write('Data for the Ingredient table is loaded!')

    def handle(self, *args, **options):
        self._load_ingredient()
