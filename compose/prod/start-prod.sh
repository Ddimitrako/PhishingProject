#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset

echo "Starting scripts"



if [ -z "${SQL_USER}" ]; then
    base_postgres_image_default_user='postgres'
    export POSTGRES_USER="${base_postgres_image_default_user}"
fi
export DATABASE_URL="postgres://${SQL_USER}:${SQL_PASSWORD}@${SQL_HOST}:${SQL_PORT}/${SQL_DATABASE}"

postgres_ready() {
python << END
import sys

import psycopg2

try:
    psycopg2.connect(
        dbname="${SQL_DATABASE}",
        user="${SQL_USER}",
        password="${SQL_PASSWORD}",
        host="${SQL_HOST}",
        port="${SQL_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

exec "$@"


echo "Migrating..."
python manage.py migrate --noinput

echo "Collecting the static files"
python manage.py collectstatic --noinput

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

echo "Importing Insider Threats Model"
python manage.py insert_insider

#echo "Importing General Recommendations"
#python manage.py insert_general_recommendations
#
#echo "Importing Insider Threats Recommendations"
#python manage.py insert_insider_recommendations

echo "Importing all recommendations (general and insider) "
python manage.py loaddata recommendations.json

echo "Importing the insider recommendations connection with insider threats"
python manage.py loaddata recommendation_insider_threat.json

echo "Importing SBAM Tests"
python manage.py loaddata tests.json

echo "Importing the demo emails for Phishing Quiz"
python manage.py loaddata demo_emails.json

echo "Importing the demo emails for Phishing Simulation Quiz"
python manage.py generate_sim_email

echo "Starting service for scheduled tasks"
python manage.py qcluster &

echo "Starting the server..."
gunicorn sbam.wsgi:application --bind 0.0.0.0:8080 --workers=${WEB_CONCURRENCY}
