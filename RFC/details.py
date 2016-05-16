# -*- coding: utf-8 -*-

import MySQLdb as pymysql
from RFC.models import *
import constants as C

QUERY = \
    """
select 
o.dt, 
ops.FineName as "OP A",
COALESCE(hus.name, "DIRECT") as "Hub A",
COALESCE(hud.name, "DIRECT") as "Hub B",
opd.FineName as "OP B",
o.status, 
o.cnt
from OPER_STAT o
left join operators ops
on ops.ID=o.src_oper_id
left join operators opd
on opd.ID=o.dst_oper_id
left join hubs hus
on hus.ID=o.src_hub_id
left join hubs hud
on hud.ID=o.dst_hub_id
where o.dt >= '{date}'
and ((
o.src_oper_id = {oper_our} and o.dst_oper_id = {oper_foreign}
)
or (
o.dst_oper_id = {oper_our} and o.src_oper_id = {oper_foreign}
))
order by -o.dt, o.status, ops.FineName
"""

DELIVERY_STATUSES = {
    2: "Delivered"
}


def stat(date, oper_our, oper_foreign):
    # date must be string formatted in 'Y-m-d'
    try:
        conn = pymysql.connect(host=C.EXTERNAL_DB['HOST'],
                               port=C.EXTERNAL_DB['PORT'],
                               db=C.EXTERNAL_DB['DB_NAME'],
                               user=C.EXTERNAL_DB['USER'],
                               connect_timeout=C.EXTERNAL_DB['TIMEOUT'])
    except pymysql.err.OperationalError:
        return 0, "Error connecting to DB."
    print "Connected!"
    query = QUERY.format(date=date, \
                         oper_our=oper_our, \
                         oper_foreign=oper_foreign)
    print query
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    result = []
    for row in rows:
        sql_dict = dict(day=row[0],
                        op_a=row[1],
                        hub_a=row[2],
                        hub_b=row[3],
                        op_b=row[4],
                        status=DELIVERY_STATUSES.get(row[5], "Undelivered"),
                        cnt=row[6]
                        )
        result.append(sql_dict)

    conn.close()
    return 1, result

