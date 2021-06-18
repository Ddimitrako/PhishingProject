from django.core.management.base import BaseCommand, CommandError
import json
import csv
from sbam_app.models import *


class Command(BaseCommand):
	def handle(self, *args, **options):

		with open('sbam_app/recommendations/insider_rems.csv') as read_obj:
			csv_reader = csv.reader(read_obj, delimiter=';')
			headers = next(csv_reader, None)
			print(headers, '\n', '-------------')
			for row in csv_reader:
				print(row[0], row[1], row[2].split('.'))
