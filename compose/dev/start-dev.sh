#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset


echo "Waiting for postgres..."

while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"


echo "Migrating..."
python manage.py migrate --noinput

echo "Initiating the admin"
python manage.py initadmin

echo "Generate the multi-lingual context"
python manage.py compilemessages 

echo "Loading the Security Culture Model"
python manage.py loaddata "sbam_app/fixtures/security_culture_model.json"

echo "Generating the default question types"
python manage.py generate_default_question_types

echo "Importing the questionnaires"
python manage.py import_questionnaire

echo "Importing the Mitre Attack Model"
python manage.py insert_mittre

echo "Importing SBAM Tests"
python manage.py loaddata tests.json

echo "Importing the demo emails for Phishing Quiz"
python manage.py loaddata demo_emails.json

echo "Importing the demo emails for Phishing Simulation Quiz"
python manage.py generate_sim_email

echo "Starting service for scheduled tasks"
python manage.py qcluster &

echo "Starting the server..."
python manage.py runserver 0.0.0.0:8000
