from django.core.management.base import BaseCommand, CommandError
import json
import csv
from sbam_app.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        types = ['enterprise', 'ics']
        # Mitigations and Attack Patterns
        for t in types:
            print('------------------------------------\n',t, '\n------------------------------------\n')
            with open('sbam_app/mitre/{0}-attack.json'.format(t), encoding="utf8") as f:
                data = json.load(f)

            print(len(data['objects']))

            mitigations = []
            attack_patterns = []

            for obj in data['objects']:
                if obj['type'] == 'course-of-action' and str(obj['external_references'][0]['external_id']).startswith('M'):
                    mitigations.append(obj)
                elif obj['type'] == 'attack-pattern':
                    attack_patterns.append(obj)

            for m in mitigations:
                # print('MITIGATION', m['external_references'][0]['url'])
                mitigation, created = Mitigation.objects.get_or_create(
                    mittre_id=m['external_references'][0]['external_id'],
                    mittre_json_id=m['id'],
                    # type=t,
                )
                mitigation.name = m['name']
                mitigation.description = m['description']
                mitigation.url = m['external_references'][0]['url']
                # print(mitigation.name)
                mitigation.save()

            for ap in attack_patterns:
                print('ATTACK', ap['external_references'][0]['url'])
                attack_pattern, created = AttackPattern.objects.get_or_create(
                    mittre_id=ap['external_references'][0]['external_id'],
                    mittre_json_id=ap['id'],
                    # type=t,
                )
                attack_pattern.name = ap['name']
                attack_pattern.url = ap['external_references'][0]['url']
                try:
                    attack_pattern.description = ap['description']
                except:
                    attack_pattern.description = ''
                # print(attack_pattern.name)
                attack_pattern.save()

            relations = []
            for obj in data['objects']:
                if obj['type'] == 'relationship' and obj['relationship_type'] == 'mitigates':
                    relations.append(obj)

            for r in relations:
                m = r['source_ref']
                # print(m)
                try:
                    mitigation = Mitigation.objects.get(mittre_json_id=m)
                except:
                    print(m)
                    continue
                ap = r['target_ref']
                # print(ap)
                attack_pattern = AttackPattern.objects.get(mittre_json_id=ap)
                mitigation.attack_patterns.add(attack_pattern)
                mitigation.save()

            # Domains and Mitigations
            with open('sbam_app/mitre/domains_mitigations_{0}.csv'.format(t), 'r') as read_obj:
                # pass the file object to reader() to get the reader object
                csv_reader = csv.reader(read_obj, delimiter=';')
                headers = next(csv_reader, None)
                # Iterate over each row in the csv using reader object
                for row in csv_reader:
                    # row variable is a list that represents a row in csv
                    mittre_id = row[0]
                    mitigation_name = row[1]
                    mitigation_description = row[3]
                    if row[4] == "":
                        continue
                    for x in row[4].split('\n'):
                        model_parts = x.replace('"', "").split('->')
                        level = 0 if model_parts[0] == 'Org.' else 1
                        dimension_name = model_parts[1]
                        domain_name = model_parts[2]

                        print(dimension_name, domain_name)

                        mitigation = Mitigation.objects.get(
                            mittre_id=mittre_id)
                        dimension = Dimension.objects.get(
                            level=level, title=dimension_name)
                        # print(dimension.title)
                        domain = Domain.objects.get(
                            dimension=dimension, title=domain_name)
                        # print(domain.title)
                        mitigation.domains.add(domain)
                        mitigation.save()
