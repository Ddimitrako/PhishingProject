from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from email_simulation import models as sim_models
import json


class Command(BaseCommand):
	def handle(self, *args, **options):
		data = None

		if not sim_models.SimEmail.objects.filter(title='Demo Email').exists():
			with open('sbam_app/fixtures/sim_email_foronline.json') as f:
				data = json.load(f)
				f.close()

			email_content = data[0]['fields']['content']

			email_content = email_content.replace('encrypted_url', settings.ENCRYPTED_ENDPOINT)
			print(email_content)
			demo_email = sim_models.SimEmail(title='Demo Email', content=email_content, subject='Demo subject')
			demo_email.save()
			print("Email created!")
