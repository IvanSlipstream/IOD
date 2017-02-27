# -*- coding: utf-8 -*-

from RFC.models import *


def is_override(rfc_new, rfc_old):
    """
    :type rfc_new: ChangeRequest
    :type rfc_old: ChangeRequest
    """
    if rfc_new.oper_our != rfc_old.oper_our or rfc_new.oper_foreign != rfc_old.oper_foreign:
        return False
    if rfc_new.direction % 2 >= rfc_old.direction % 2 and rfc_new.direction // 2 >= rfc_old.direction // 2:
        return True
    else:
        return False


def find_overriden(rfc_new):
    """

    :type rfc_new: ChangeRequest
    """
    result = []
    for rfc_old in ChangeRequest.objects.all()\
            .exclude(id=rfc_new.id)\
            .filter(cur_state__in=[0,1,2]):
        if is_override(rfc_new, rfc_old):
            result += [rfc_old]
    return result
