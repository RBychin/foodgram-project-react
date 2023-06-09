import csv
import logging
import os

from django.core.management.base import BaseCommand
from django.db import DatabaseError, IntegrityError
from core.models import Ingredient
from foodgram.settings import BASE_DIR

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
logger.addHandler(sh)


FILE = os.path.join(
    BASE_DIR.parent.parent,
    'data/ingredients.csv'
)


def open_csv(file):
    try:
        with open(FILE, 'r',
                  encoding='utf-8') as r_file:
            reader = csv.DictReader(
                r_file,
                fieldnames=[
                    'name',
                    'measurement_unit'
                ],
                delimiter=',')
            create_obj(reader)
    except FileNotFoundError:
        logger.error('Файл не найден.')


def create_obj(reader):
    try:
        objects = [Ingredient(
            name=i['name'],
            measurement_unit=i['measurement_unit']
        ) for i in reader]
        Ingredient.objects.bulk_create(objects)
    except IntegrityError:
        logger.error('Ошибка уникальности')
    except DatabaseError as er:
        logger.error(f'Ошибка: {er}')
    else:
        logger.info(f'Успех, добавлено '
                    f'{reader.line_num} записей.')


class Command(BaseCommand):
    help = f'Загружает данные из csv таблицы {FILE}'

    def handle(self, *args, **options):
        try:
            open_csv(FILE)
        except TypeError:
            logger.error(f'Ошибка, проверьте '
                         f'наличие файла по адресу {FILE}')
