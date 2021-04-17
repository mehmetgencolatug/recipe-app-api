import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until DB is available"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for DB...")
        db_conn = None

        while not db_conn:
            try:
                db_conn = connections["default"]
            except OperationalError:
                self.stdout.write("DB is unavailable. Waiting for 1 sec...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("DB connected, now available!"))
