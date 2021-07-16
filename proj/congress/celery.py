import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
#
# You don’t need this line, but it saves you from always passing in the
# settings module to the celery program. It must always come before creating
# the app instances, as is what we do next.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'congress.settings')

# This is our instance of the library, you can have many instances but there’s
# probably no reason for that when using Django.
app = Celery('congress')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
#
# We also add the Django settings module as a configuration source for Celery.
# This means that you don’t have to use multiple configuration files, and
# instead configure Celery directly from the Django settings; but you can also
# separate them if wanted.
#
# The uppercase name-space means that all Celery configuration options must be
# specified in uppercase instead of lowercase, and start with 'CELERY_'.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
