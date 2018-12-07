from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from saleboxdjango.models import BasketWishlist


class Command(BaseCommand):
    def handle(self, *args, **options):
        expired_keys = Session \
                        .objects \
                        .filter(expire_date__gte=timezone.now()) \
                        .values_list('session_key', flat=True)

        print(list(expired_keys))

        b = BasketWishlist \
                .objects \
                .filter(session__in=list(expired_keys))

        print(b)
