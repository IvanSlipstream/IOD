from django.test import TestCase
from RFC.models import change_request

# Create your tests here.

def date_test():
	example = change_request.objects.all()[1]
	return render_to_response('dateTest.html', {'example': example})
	