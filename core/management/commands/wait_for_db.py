import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to pause execution until db is available"""
    def handle(self, *args, **options):
        # check if db is availble then cleanly exit
        self.stdout.write('Waiting for db...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('db unavailable, waiting 1 second')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('db ready'))
