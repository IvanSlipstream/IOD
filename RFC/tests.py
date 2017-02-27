from django.shortcuts import render_to_response
from django.test import TestCase

from RFC import track
from RFC.models import *


# Create your tests here.

class TrackerTestCase(TestCase):
    def setUp(self):
        self.tracker = Tracker()
        rfc = ChangeRequest.objects.get(id=28)
        self.tracker.rfc = rfc
        self.tracker.count = 5
        track.is_tracker_fulfilled(self.tracker)

    def runTest(self):
        self.assertEqual(track.is_tracker_fulfilled(self.tracker))


class OverrideTestCase(TestCase):
    def __init__(self, methodName='runTest'):
        super(OverrideTestCase, self).__init__(methodName='runTest')
        self.rfc_new = []
        self.rfc_old = []

    def setUp(self):
        oper_our = Operator()
        oper_foreign = Operator()
        for i in range(4):
            self.rfc_old += [ChangeRequest(oper_our=oper_our, oper_foreign=oper_foreign, direction=i)]
            self.rfc_new += [ChangeRequest(oper_our=oper_our, oper_foreign=oper_foreign, direction=i)]

    def runTest(self):
        from RFC import override
        expected = [
            [True, True, True, True],
            [False, True, False, True],
            [False, False, True, True],
            [False, False, False, True]
        ]

        for i in range(4):
            for j in range(4):
                self.assertEqual(override.is_override(self.rfc_new[j], self.rfc_old[i]), expected[i][j],
                                 "New: %d, old: %d" % (j,i))