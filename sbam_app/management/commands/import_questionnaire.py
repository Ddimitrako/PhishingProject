import csv
import os
from json import loads

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from sbam_app.models import *

if os.name == 'nt':
    DEFAUL_BASE_DIR = '.\sbam_app\content\questionnaires'
else:
    DEFAUL_BASE_DIR = './sbam_app/content/questionnaires'


class Command(BaseCommand):
    help = 'Import/Update questionnaires'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', type=str, help=_('The tab-separated file of the questionnaire'))
        parser.add_argument('-d', '--dir', type=str, help=_('The directory hosting questionnaires'))

    def handle(self, *args, **kwargs):
        
        filename = kwargs['file']
        dir = kwargs['dir']

        directory = dir if dir else DEFAUL_BASE_DIR

        if filename:
            with transaction.atomic():
                self.import_quest(filename)
            self.stdout.write(self.style.SUCCESS('Successfully imported questionnaire from file: ' + filename))
        elif directory:
            for root, directories, files in os.walk(directory):
                for file in files:
                    with transaction.atomic():
                        filepath = os.path.join(root, file)
                        self.import_quest(filepath)
                        self.stdout.write(self.style.SUCCESS('Successfully imported: ' + file))
            self.stdout.write(self.style.SUCCESS('Successfully imported all questionnaires from root directory: ' + directory))
        else:
            self.stdout.write(self.style.ERROR('No filename specified or all flag used!'))


    def import_quest(self, filename):
        file_parts = filename.split('__')
        domain = file_parts[1].replace('_', ' ')
        questionnaire_title = file_parts[2].split('.')[0].replace('_', ' ')
        print('Importing questionnaire with title: "' + questionnaire_title + '" in security domain: "' + domain + '"')

        try:
            questionnaire = Questionnaire.objects.get(
                title=questionnaire_title,
                domain=Domain.objects.get(title__iexact=domain)
            )
        except Questionnaire.DoesNotExist:
            questionnaire = Questionnaire(
                title=questionnaire_title,
                domain=Domain.objects.get(title__iexact=domain)
            )
            questionnaire.save()

        fd = open(filename)
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        headers = next(rd)
        # Check file as empty
        if headers == None:
            raise Exception("The file is empty")

        num_of_languages = int(len(headers[2:]) / 2)

        # Iterate over each row after the header in the csv
        for i, row in enumerate(rd):
            #print(row)
            if len([x for x in row if x.strip() != '']) == 0:
                continue
            # print(row[0])
            q_id_in_questionnaire = int(row[0])
            try:
                question = Question.objects.get(
                    questionnaire=questionnaire,
                    id_in_questionnaire=q_id_in_questionnaire
                )
                created_question = False
            except Question.DoesNotExist:
                question = Question(questionnaire=questionnaire,
                                    id_in_questionnaire=q_id_in_questionnaire
                                    )
                created_question = True

            q_order = i
            question.order = q_order

            # Check if it's a custom question and if yes, IF it is a newly created one (and not updated), then create new question type and options
            q_type = row[1]
            # import pdb
            # pdb.set_trace()
            if 'CUSTOM' not in q_type:  # if not custom get the default type
                question_type = QuestionType.objects.get(type=q_type)
                q_is_custom = False
            else:  # if custom check create or update the question type
                if q_type == 'CUSTOM_R':
                    takes_multiple = False
                else:
                    takes_multiple = True

                if created_question:
                    question_type = QuestionType(type=q_type, takes_multiple=takes_multiple)
                    question_type.save()
                else:
                    question_type = question.question_type
                q_is_custom = True
            question.question_type = question_type

            # Iterate the languages to set the question and options texts/values
            for lang_idx in range(1, num_of_languages + 1):
                lang_col_text_idx = lang_idx * 2
                lang_col_options_idx = lang_idx * 2 + 1

                lang = headers[lang_col_text_idx].split('_')[1]
                #print('Language {0} is {1}'.format(str(lang_idx), lang))

                # set the text attr of the language i.e. text_en for the English text
                q_lang_text_field = headers[lang_col_text_idx]
                q_lang_text = row[lang_col_text_idx]
                setattr(question, q_lang_text_field, q_lang_text)

                # if it is a custom question type, update or create the options
                if q_is_custom:
                    #print(row[lang_col_options_idx])
                    options_list = loads(row[lang_col_options_idx])
                    for opt in options_list:
                        opt_id_in_question = int(opt[0])
                        opt_order = int(opt[1])
                        opt_text = str(opt[2])
                        opt_val = float(opt[3])

                        try:
                            question_option = QuestionOption.objects.get(
                                question_type=question_type,
                                id_in_question=opt_id_in_question
                            )
                        except QuestionOption.DoesNotExist:
                            question_option = QuestionOption(
                                question_type=question_type,
                                id_in_question=opt_id_in_question
                            )
                        setattr(question_option, 'text_' + lang, opt_text)
                        question_option.value = opt_val
                        question_option.order = opt_order
                        question_option.save()

            question.save()
