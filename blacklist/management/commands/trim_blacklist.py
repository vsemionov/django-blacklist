from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import F
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
        self.stdout.write('Deleting expired rules')

        created_age = timedelta(days=options['created'])
        expired_age = timedelta(days=options['expired'])

        current_time = now()

        rules = Rule.objects.filter(created__lte=(current_time - F('duration')))
        rules = rules.filter(created__lte=(current_time - created_age))
        rules = rules.filter(created__lte=(current_time - expired_age - F('duration')))

        deleted = rules.delete()
        num_deleted = deleted[1].get('%s.%s' % (Rule._meta.app_label, Rule._meta.object_name), 0)

        self.stdout.write(self.style.SUCCESS('Deleted %d rule(s).' % num_deleted))
