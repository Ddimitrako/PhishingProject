from django.core.management.base import BaseCommand, CommandError
import json
import csv
from sbam_app.models import *

class Command(BaseCommand):
	def handle(self, *args, **options):

		with open('sbam_app/insider_threat/factors.csv', 'r') as read_obj:
			csv_reader = csv.reader(read_obj, delimiter=';')
			headers = next(csv_reader, None)
			for row in csv_reader:
				f_name = row[0]
				f_desc = row[1]
				f_domains = row[2].split('\n')

				print('Name', f_name)
				print('Desc', f_desc)
				print('Domains', f_domains)

				related_domains = Domain.objects.filter(title__in=f_domains)
				factor = InsiderThreatsFactor(name=f_name, description=f_desc)
				factor.save()
				for domain in related_domains:
					factor.domains.add(domain)


		with open('sbam_app/insider_threat/thread_types.csv', 'r') as read_obj:
			csv_reader = csv.reader(read_obj, delimiter=';')
			headers = next(csv_reader, None)

			for row in csv_reader:
				t_name = row[0]
				t_desc = row[1]
				sub_types = row[2].split('\n')
				sub_types_desc = row[3].split('\n')
				factors = row[4].split('\n')

				related_factors = InsiderThreatsFactor.objects.filter(name__in=factors)

				print('Name', t_name)
				print('Desc', t_desc)
				print('Sub_types', sub_types)
				print('Desc', sub_types_desc)
				print('Factors', factors)

				thread = InsiderThreat(name=t_name, description=t_desc)
				thread.save()

				for factor in related_factors:
					factor.insider_threat.add(thread)
				for s_type, s_type_desc in zip(sub_types, sub_types_desc):
					sb_type = InsiderThreatSubType(name=s_type, description=s_type_desc, insider_threat=thread)
					sb_type.save()

