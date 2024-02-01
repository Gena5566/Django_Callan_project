# import_csv.py

"""вы должны использовать абсолютный путь к файлу в командной строке
 Например: python manage.py import_csv /Users/n.a./PycharmProjects/pythonProject10/
 pythonProject/pythonProject/Django_Callan/
 DjangoCallanProject/
 Word_stage_4_for_Django_Page1.csv)"""

import csv
from django.core.management.base import BaseCommand
from callanapp.models import Word  # Используйте правильное имя модели

class Command(BaseCommand):
    help = 'Import words from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row

            for row in csv_reader:
                russian_word, english_translation, level = row
                Word.objects.create(
                    russian_word=russian_word.strip(),
                    english_translation=english_translation.strip(),
                    level=level.strip()
                )

        self.stdout.write(self.style.SUCCESS('Data imported successfully.'))

