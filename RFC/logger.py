# -*- coding: utf-8 -*-

from RFC.constants import ACTION_LOGGER_FILE
from django.conf import settings
from datetime import datetime

ACTION_LOG_IN = 1
ACTION_LOG_OUT = 2
ACTION_SYNC_OPERATORS = 3

ACTION_ADD_RFC = 4
ACTION_REMOVE_RFC = 5
ACTION_CONFIRM_ROUTE = 6
ACTION_CONFIRM_TRAFFIC = 7

def log_action(user, rfc=None, action=0):
    # TODO: make pretty foemat for string
    string_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    filename = settings.BASE_DIR + '/' + ACTION_LOGGER_FILE
    with open(filename, 'a') as f:
	if action==ACTION_LOG_IN:
	    f.write( "%s: %s has logged in.\n" % (string_time, user) )
	
