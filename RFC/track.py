from datetime import date, timedelta

from RFC import details
from RFC.models import Tracker


def is_tracker_fulfiled(tracker):
    checking_date = (date.today() - timedelta(days=1))
    statistics = details.stat(checking_date, tracker.rfc.oper_our._id, tracker.rfc.oper_foreign._id)
    if tracker.direction == Tracker.DIRECTION_FORWARD:
        src_key = 'op_a'
        dst_key = 'op_b'
    elif tracker.direction == Tracker.DIRECTION_BACKWARD:
        src_key = 'op_b'
        dst_key = 'op_a'
    else:
        return False
    if not statistics[0]:
        return False
    for stat_instance in statistics[1]:
        if stat_instance.get('day') != checking_date:
            continue
        if stat_instance.get('status') != "Delivered":
            continue
        if tracker.route is not None and tracker.route != stat_instance.get('hub_b'):
            continue
        if stat_instance.get(src_key) == tracker.rfc.oper_our.fineName and stat_instance.get(dst_key) == tracker.rfc.oper_foreign.fineName:
            if stat_instance.get('cnt', 0) >= tracker.count:
                return True
    return False