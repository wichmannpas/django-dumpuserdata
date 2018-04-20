from pprint import pprint

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.core.serializers import serialize

from dumpuserdata.dumpuserdata import dump_data


class Command(BaseCommand):
    help = 'Dump all data associated to a user.'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='The username of the user.')

    def handle(self, *args, **options):
        user = get_user_model().objects.get(username=options['username'])
        user_data = dump_data(user)
        #return serialize('json', relevant_rows)
        user_data = {
            key: serialize('json', value)
            for key, value in user_data.items()
        }
        pprint(user_data)
