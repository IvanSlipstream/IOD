from django.core.management import BaseCommand
from django.core.mail import send_mail

from RFC.models import *

import RFC.constants as C


class Command(BaseCommand):
    help = """Usage: \npython manage.py reminders SERVER_ADDRESS[:PORT]
SERVER_ADDRESS is used in a hyperlink to the RFC in mail notifications.
Examples: '10.10.222.222:8080', 'iod.mycompany.com'.
        """

    def prepair_mail_for_user(self, user, link):
        """

        :type user: User
        """
        mail = ''
        rfcs = ChangeRequest.objects.filter(author=user).filter(cur_state=1).order_by('-dt')
        for rfc in rfcs:
            mail += "%s\t%s\tReason: %s\r\n" % (link + str(rfc.id) + '/', rfc, rfc.tracker_comment)
        if len(mail):
            mail = "Dear %s %s, \r\nThis is a report on your pending RFC.\r\n" % (
            user.first_name, user.last_name) + mail
            send_mail("RFCs not completed", mail, C.RFC_TRACKER_SENDER, [user.email])

    def handle(self, *args, **options):
        if not len(args):
            self.stderr.write("Invalid syntax.")
            return
        for user in User.objects.all():
            link = "http://%s/detail/" % args[0]
            self.prepair_mail_for_user(user, link)
