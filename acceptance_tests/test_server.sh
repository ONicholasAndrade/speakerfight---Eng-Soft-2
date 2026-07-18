#!/bin/sh
set -e

cp speakerfight/ci_local_settings.py speakerfight/local_settings.py

python manage.py check
python manage.py test -v 2