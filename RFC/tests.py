from django.shortcuts import render_to_response
from django.test import TestCase

from RFC import track
from RFC.models import *


# Create your tests here.

def date_test():
	example = ChangeRequest.objects.all()[1]
	return render_to_response('dateTest.html', {'example': example})

class TrackerTestCase(TestCase):
	def setUp(self):
		self.tracker = Tracker()
		rfc = ChangeRequest.objects.get(id=28)
		self.tracker.rfc = rfc
		self.tracker.count = 5
		track.is_tracker_fulfilled(self.tracker)

	def test_tracker(self):
		self.assertEqual(track.is_tracker_fulfilled(self.tracker))