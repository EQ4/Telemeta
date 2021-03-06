#!/bin/sh

# paths
app_dir='/opt/Telemeta'
sandbox='/home/sandbox'
manage=$sandbox'/manage.py'
wsgi=$sandbox'/wsgi.py'

# stating apps
pip install django-haystack elasticsearch

# waiting for other services
sh $app_dir/examples/deploy/wait.sh

# Starting celery worker with the --autoreload option will enable the worker to watch for file system changes
# This is an experimental feature intended for use in development only
# see http://celery.readthedocs.org/en/latest/userguide/workers.html#autoreloading
$manage celery worker --autoreload -A celery_app
