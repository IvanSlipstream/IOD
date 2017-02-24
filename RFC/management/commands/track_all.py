from django.core.management import BaseCommand
from django.core.mail import send_mail

from RFC import track
from RFC.models import Tracker

import RFC.constants as C


class Command(BaseCommand):
    help = """Usage: \npython manage.py track_all SERVER_ADDRESS[:PORT]
SERVER_ADDRESS is used in a hyperlink to the RFC in mail notifications.
Examples: '10.10.222.222:8080', 'iod.mycompany.com'.
    """

    def handle(self, *args, **options):
        mail = u''
        if not len(args):
            self.stderr.write("Invalid syntax.")
            return
        link_template = "http://%s/detail/%d/"
        for tracker in Tracker.objects.all().filter(fulfilled=False):
            if track.is_tracker_fulfilled_immediate(tracker):
                tracker.fulfilled = True
                tracker.save()
                self.stdout.write("Tracker %d is fulfilled.\n" % tracker.id)
                link = link_template % (args[0], tracker.rfc.id)
                mail += "Tracker for rfc %s is fulfilled.\n" % link
            else:
                self.stderr.write("Tracker %d is not fulfilled.\n" % tracker.id)
        if len(mail):
            send_mail("New trackers have been fulfilled", mail, C.RFC_TRACKER_SENDER, C.RFC_TRACKER_RECIPIENT_LIST)
