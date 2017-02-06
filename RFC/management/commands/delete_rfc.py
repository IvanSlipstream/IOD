from django.core.management.base import BaseCommand, CommandError
from RFC.models import *


class Command(BaseCommand):
    help = """Usage: \npython manage.py delete_rfc RFC_ID
RFC_ID could be harvested from URL 
e.g. http://iod.mycompany.com/detail/73/ means RFC_ID is 73.
    """

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Invalid syntax.\n" + self.help)
        try:
            _id = args[0]
            rfc = ChangeRequest.objects.get(id=_id)
            rfc.delete()
            self.stdout.write("RFC#%s was successfully deleted." % _id)
        except ChangeRequest.DoesNotExist:
            raise CommandError("RFC not found.")
        except ValueError:
            raise CommandError("Invalid RFC number.")
