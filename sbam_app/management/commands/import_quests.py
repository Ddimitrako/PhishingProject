import os
from django.core.management.base import BaseCommand
from django.core.management import call_command

BASE_DIR = '.\sbam_app\content\questionnaires'

class Command(BaseCommand):
    help = 'Import all available questionnaires'

    def handle(self, *args, **kwargs):
        for level in  os.listdir(BASE_DIR):
            for sub_dir in os.listdir(BASE_DIR+'\\'+level):
                for quest in os.listdir(BASE_DIR+'\\'+level+'\\'+sub_dir):
                    call_command('import_questionnaire', BASE_DIR+'\\'+level+'\\'+sub_dir+'\\'+quest)
                    # os.system("manage.py import_questionnaire "+BASE_DIR+'\\'+level+'\\'+sub_dir+'\\'+quest)
