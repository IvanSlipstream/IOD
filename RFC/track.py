from datetime import date, timedelta, datetime

from RFC import details
from RFC.models import Tracker, ChangeRequest

import RFC.constants as C
import pymysql


def is_tracker_fulfilled(tracker):
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
        if stat_instance.get(src_key) == tracker.rfc.oper_our.fineName and stat_instance.get(
                dst_key) == tracker.rfc.oper_foreign.fineName:
            if stat_instance.get('cnt', 0) >= tracker.count:
                return True
    return False


def is_tracker_fulfilled_immediate(tracker):
    checking_date = (datetime.now() - timedelta(hours=2)).date().strftime('%Y-%m-%d')
    route_filter = ""
    source = 0
    destination = 0
    result = False
    query_template = '''SELECT sum(cnt) FROM OPER_STAT o
LEFT JOIN hubs hs ON hs.ID = o.src_hub_id
LEFT JOIN hubs hd ON hd.ID = o.dst_hub_id
WHERE
o.dt="{checking_date}"
AND o.status=2
AND o.src_oper_id={source}
AND o.dst_oper_id={destination}
{route_filter}'''
    if tracker.direction == Tracker.DIRECTION_FORWARD:
        source = tracker.rfc.oper_our._id
        destination = tracker.rfc.oper_foreign._id
        if tracker.route:
            route_filter = 'AND COALESCE(hd.NAME, "DIRECT")="%s"' % tracker.route
    if tracker.direction == Tracker.DIRECTION_BACKWARD:
        source = tracker.rfc.oper_foreign._id
        destination = tracker.rfc.oper_our._id
        if tracker.route:
            route_filter = 'AND COALESCE(hs.NAME, "DIRECT")="%s"' % tracker.route
    with pymysql.connect(host=C.EXTERNAL_DB['HOST'],
                         port=C.EXTERNAL_DB['PORT'],
                         db=C.EXTERNAL_DB['DB_NAME'],
                         user=C.EXTERNAL_DB['USER'],
                         connect_timeout=C.EXTERNAL_DB['TIMEOUT'],
                         passwd=C.EXTERNAL_DB['PASSWD']) as cur:
        query = query_template.format(source=source, destination=destination, route_filter=route_filter,
                                                checking_date=checking_date)
        cur.execute(query)
        if cur.rowcount:
            cnt = cur.fetchone()[0]
            result = (cnt >= tracker.count)
    return result
