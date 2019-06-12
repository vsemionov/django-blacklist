from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from ...models import Rule


class Command(BaseCommand):
    help = 'Trims the blacklist'

    def add_arguments(self, parser):
        parser.add_argument('-c', '--created', type=int, default=0,
            help='created days ago; default: 0')
        parser.add_argument('-e', '--expired', type=int, default=0,
            help='expired days ago; default: 0')

    def handle(self, *args, **options):
        self.stdout.write('Removing expired rules')

        created_time = timedelta(days=options['created'])
        expired_time = timedelta(days=options['expired'])

        current_time = now()

        num_rules = 0

        for rule in Rule.objects.all():
            if rule.is_active():
                continue

            if current_time < rule.created + created_time:
                continue
            if current_time < rule.get_expires() + expired_time:
                continue

            rule.delete()

            num_rules += 1

        self.stdout.write(self.style.SUCCESS('Removed %d rules.' % num_rules))
