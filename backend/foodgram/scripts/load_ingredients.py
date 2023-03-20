import csv
from django.conf import settings
from recipes.models import Ingredient


def run():
    with open(f'{settings.BASE_DIR}/api/static/data/ingredients.csv') as file:
        reader = csv.reader(file)
        for row in reader:
            ingredient = Ingredient(
                name=row[0],
                measurement_unit=row[1]
            )
            ingredient.save()
