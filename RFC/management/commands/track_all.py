from django.core.management import BaseCommand
from django.core.mail import send_mail

from RFC import track
from RFC.models import Tracker

import RFC.constants as C

class Command(BaseCommand):
    help = """Usage: \npython manage.py delete_rfc RFC_ID
RFC_ID could be harvested from URL
e.g. http://iod.mycompany.com/detail/73/ means RFC_ID is 73.
    """

    def handle(self, *args, **options):
        mail = u''
        for tracker in Tracker.objects.all().filter(fulfilled=False):
            if track.is_tracker_fulfilled_immediate(tracker):
                tracker.fulfilled = True
                tracker.save()
                self.stdout.write("Tracker %d is fulfilled.\n" % tracker.id)
                mail+="Tracker for rfc #%d is fulfilled.\n" % tracker.rfc.id
            else:
                self.stderr.write("Tracker %d is not fulfilled.\n" % tracker.id)
        send_mail("New trackers have been fulfilled", mail, C.RFC_TRACKER_SENDER, C.RFC_TRACKER_RECIPIENT_LIST)

