# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User


class Operator(models.Model):
    _id = models.IntegerField(primary_key=True)
    fineName = models.CharField(max_length=50)
    isDirect = models.BooleanField(default=False)
    e212 = models.CharField(max_length=10, default="no e212")

    def __str__(self):
        return ('%s %s' % (self.fineName[:25], self.e212)).encode("utf-8")


class UserMeta(models.Model):
    user_reference = models.OneToOneField(User)
    position = models.CharField(max_length=30, default=u'Unknown Employee')
    phone_work = models.CharField(max_length=20)
    phone_mob = models.CharField(max_length=20)

    def __str__(self):
        return ('%s %s, %s' % (
            self.user_reference.first_name,
            self.user_reference.last_name,
            self.position,
        )).encode("utf-8")


class ChangeRequest(models.Model):
    author = models.ForeignKey(User)
    dt = models.DateField()
    comments = models.CharField(max_length=60)
    PRIO_CHOICE = (
        (1, '1st'),
        (2, '2nd'),
        (3, '3rd'),
        (0, 'Last'),
    )
    prio = models.IntegerField(choices=PRIO_CHOICE, default=1)
    peer_hub = models.CharField(max_length=20, default="DIRECT")
    oper_our = models.ForeignKey('Operator', related_name='+', on_delete=models.PROTECT)
    oper_foreign = models.ForeignKey('Operator', related_name='+', on_delete=models.PROTECT)
    DIR_CHOICE = (
        (0, "RATE_ONLY"),
        (1, "FORWARD"),
        (2, "BACKWARD"),
        (3, "TWO_WAY"),
    )
    direction = models.IntegerField(choices=DIR_CHOICE, default=0)
    STATE_CHOICE = (
        (0, "NEW"),
        (1, "IMPLEMENTED"),
        (2, "COMPLETED"),
        (3, "UNTRACKABLE"),
        (4, "OVERRIDEN"),
        (5, "REJECTED"),
    )
    cur_state = models.IntegerField(choices=STATE_CHOICE, default=0)
    tracker_comment = models.CharField(max_length=60)

    def priority(self):
        return dict(self.PRIO_CHOICE).get(self.prio, "Last")

    def __str__(self):
        delimiters = {
            0: "-",
            1: "->",
            2: "<-",
            3: "<->"
        }
        return '%s: %s %s %s %s %s' % (
            self.dt.isoformat(),
            self.oper_our,
            delimiters.get(self.direction),
            self.peer_hub,
            delimiters.get(self.direction),
            self.oper_foreign
        )


class Tracker(models.Model):
    rfc = models.ForeignKey('ChangeRequest', related_name='+', on_delete=models.PROTECT)
    count = models.IntegerField(default=-1)
    route = models.TextField(max_length=30, null=True)
    DIRECTION_FORWARD = 1
    DIRECTION_BACKWARD = 2
    direction = models.IntegerField()
    fulfilled = models.BooleanField(default=False)

    def __str__(self):
        src = None
        dst = None
        if self.direction == self.DIRECTION_FORWARD:
            src = self.rfc.oper_our.fineName
            dst = self.rfc.oper_foreign.fineName
        if self.direction == self.DIRECTION_BACKWARD:
            dst = self.rfc.oper_our.fineName
            src = self.rfc.oper_foreign.fineName
        return "At least %d from %s to %s over %s" % (
            self.count,
            src,
            dst,
            (self.route if self.route else "any route")
        )


