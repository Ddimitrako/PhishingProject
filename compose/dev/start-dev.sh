#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset


echo "Waiting for postgres..."

while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"


python manage.py flush --no-input
echo "Migrating..."
python manage.py migrate --noinput

echo "Initiating the admin"
python manage.py initadmin

echo "Loading the Security Culture Model"
python manage.py loaddata "sbam_app/fixtures/security_culture_model.json"

echo "Generating the default question types"
python manage.py generate_default_question_types

echo "Starting the server..."
python manage.py runserver 0.0.0.0:8000
