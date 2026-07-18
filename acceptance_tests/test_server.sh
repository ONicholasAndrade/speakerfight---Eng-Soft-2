#!/bin/sh
set -e

python manage.py check
python manage.py test -v 2
