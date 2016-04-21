import pymysql
from RFC.models import *
import constants as C
# from django.core.exceptions import ObjectDoesNotExist


def sync():
    try:
        conn = pymysql.connect(host=C.EXTERNAL_DB['HOST'],
                               port=C.EXTERNAL_DB['PORT'],
                               db=C.EXTERNAL_DB['DB_NAME'],
                               user=C.EXTERNAL_DB['USER'],
                               connect_timeout=C.EXTERNAL_DB['TIMEOUT'])
    except pymysql.err.OperationalError:
        return 0, "Error connecting to DB."
    print "Connected!"
    query = "select id, finename, direct, e212 from operators \
		where finename!=opname and finename!=\"\""
    cur = conn.cursor()
    cur.execute(query)
    # Operator.objects.all().delete()
    existing_ops = [op._id for op in Operator.objects.all()]
    rows = cur.fetchall()
    for row in rows:
        op = Operator.objects.update_or_create(
            _id=row[0], defaults={
                'fineName': row[1].decode("utf-8", 'replace'),
                'isDirect': bool(row[2]),
                'e212': row[3]
            }
        )
        try:
            existing_ops.remove(op[0]._id)
        except ValueError:
            pass
        print "Processing: ", row
        if op[1]:
            print "Adding: ", op[0]
    if len(existing_ops):
        print "Deleting: "
    for existing_op in existing_ops:
        op = Operator.objects.get(_id=existing_op)
        op.delete()
        print op
    conn.close()
    return 1, "Operators were successfully synced."