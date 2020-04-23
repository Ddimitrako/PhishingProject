from django.core.management.base import BaseCommand, CommandError
from sbam_app import models

class Command(BaseCommand):
    help = 'Creates a question type along with the question options ex. Likert scale with 5 options'

    def add_arguments(self, parser):
        parser.add_argument('question_type', nargs='+', type=str)

    def handle(self, *args, **options):
        for question_type in options['question_type']:
            # try:
            print('Question is', question_type)
            # except