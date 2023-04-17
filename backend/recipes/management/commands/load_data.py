import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag

TAGS = (
    ('Завтрак', '#9ACD32', 'zavtrak',), ('Обед', '#FFA500', 'obed',),
    ('Ужин', '#FA8072', 'uzhin',), ('Десерт', '#4A8EF6', 'dessert',),
    )


class Command(BaseCommand):
    help = 'Загрузка данных из .csv файлов'

    def _load_ingredients(self):
        with open(
                '../data/ingredients.csv',
                encoding='utf-8'
        ) as csvfile:
            reader = csv.reader(csvfile)
            print(type(reader))
            self.stdout.write('Data loading started!')
            for name, measurement_unit in reader:
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit,
                )
        self.stdout.write('Data for the Ingredient table is loaded!')

    def _load_tags(self):
        self.stdout.write('Data loading started!')
        for name, color, slug in TAGS:
            Tag.objects.get_or_create(
                name=name,
                color=color,
                slug=slug,
            )
        self.stdout.write('Data for the Ingredient table is loaded!')

    def handle(self, *args, **options):
        self._load_ingredients()
        self._load_tags()
