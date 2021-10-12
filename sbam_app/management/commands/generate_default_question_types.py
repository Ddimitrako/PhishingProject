import json

from django.core.management.base import BaseCommand

from sbam_app.models import QuestionType, QuestionOption


class Command(BaseCommand):
    help = 'generate_default_question_types'

    def handle(self, *args, **options):
        with open('sbam_app/fixtures/default_question_types.json', encoding="utf8") as f:
            question_types = json.load(f)

        with open('sbam_app/fixtures/default_question_options.json', encoding="utf8") as f:
            question_options = json.load(f)

        languages = ['en', 'el', 'it', 'bg']

        for qt in question_types:
            try:
                qt_obj = QuestionType.objects.get(type=qt['fields']['type'])
            except QuestionType.DoesNotExist:
                qt_obj = QuestionType(type=qt['fields']['type'])
                qt_obj.save()

            for qo in question_options:
                if qo['fields']['question_type'] == qt_obj.type:
                    try:
                        qo_obj = QuestionOption.objects.get(question_type=qt_obj, value=qo['fields']['value'])
                    except QuestionOption.DoesNotExist:
                        qo_obj = QuestionOption(question_type=qt_obj)

                    for l in languages:
                        setattr(qo_obj, 'text_' + str(l), qo['fields']['text_' + str(l)])

                    qo_obj.value = qo['fields']['value']
                    qo_obj.is_active = qo['fields']['is_active']
                    qo_obj.id_in_question = qo['fields']['id_in_question']
                    qo_obj.order = qo['fields']['order']
                    qo_obj.save()
        self.stdout.write('Successfully created the default question types and their options')
