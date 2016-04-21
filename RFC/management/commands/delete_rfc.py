from django.core.management.base import BaseCommand, CommandError
from RFC.models import *

class Command(BaseCommand):
    help = "Usage: \npython manage.py delete_rfc ID_OF_RFC"

    def add_arguments(self, parser):
        parser.add_argument('rfc_id', nargs='+', type=int)

    def handle(self, *args, **options):
        # if len(args)!=1:
        #     self.stderr.write("Syntax error.")
        #     return
        try:
            _id = options['rfc_id'][0]
            rfc = ChangeRequest.objects.get(id=_id)
            rfc.delete()
            self.stdout.write("RFC#%s was successfully deleted."%_id)
        except ChangeRequest.DoesNotExist:
            raise CommandError("RFC not found.")
