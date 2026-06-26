#!/usr/bin/env bash
set -o errexit

chmod +x start.sh

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py load_datasets || true
