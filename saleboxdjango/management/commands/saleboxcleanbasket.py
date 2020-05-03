from django.core.management.base import BaseCommand, CommandError
from django.db import connection

# run this command immediately AFTER running django's clearsessions

class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM     saleboxdjango_basketwishlist
                WHERE           session IN (
                    SELECT          DISTINCT(session)
                    FROM            saleboxdjango_basketwishlist
                    WHERE           user_id IS NULL
                    AND session NOT IN (
                        SELECT          session_key
                        FROM            django_session
                    )
                )
            """)