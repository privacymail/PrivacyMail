#!/bin/bash
# Start cron because it won't on its own for some reason
service cron start
# Export env
printenv > /etc/environment

echo "Making migrations and migrating the database. "
source /opt/conda/etc/profile.d/conda.sh
conda activate privacymail
cd privacymail
python manage.py migrate --noinput 
python manage.py collectstatic --noinput

gunicorn privacymail.wsgi:application --bind 0.0.0.0:8000 --workers=4
