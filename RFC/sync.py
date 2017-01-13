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
                               passwd=C.EXTERNAL_DB['PASSWD'],
                               connect_timeout=C.EXTERNAL_DB['TIMEOUT'])
    except BaseException:
        return 0, ["Error connecting to DB."]
    sync_log = ["Connected!"]
    query = "select id, finename, direct, e212 from operators \
		where finename!=opname and finename!=\"\""
    cur = conn.cursor()
    cur.execute(query)
    # Operator.objects.all().delete()
    existing_ops = [op._id for op in Operator.objects.all()]
    rows = cur.fetchall()
    
    for row in rows:
	op_new = Operator(\
	_id=row[0], \
	fineName=row[1].decode("utf-8", 'replace'), \
	isDirect = bool(row[2]), \
	e212 = row[3])
	
	try:
	    op_old = Operator.objects.get(_id=row[0])
	    op = Operator.objects.filter(_id=row[0])
	    updated = (op_old.fineName, op_old.isDirect, op_old.e212) != \
	            (op_new.fineName, op_new.isDirect, op_new.e212)
	    if updated:
		op.update(
		    fineName=op_new.fineName, 
		    isDirect=op_new.isDirect, 
		    e212=op_new.e212
		)
		sync_log += ["Updating: " + op.__str__()]
	    try:
		existing_ops.remove(row[0])
	    except ValueError:
		pass
	except Operator.DoesNotExist:
	    op_new.save()
	    sync_log += ["Adding: " + op_new.__str__()]
	    
##################################
# for django 1.7, a bit simplier #
##################################
#        op = Operator.objects.update_or_create(
#            _id=row[0], defaults={
#                'fineName': row[1].decode("utf-8", 'replace'),
#                'isDirect': bool(row[2]),
#                'e212': row[3]
#            }
#        )
#        try:
#            existing_ops.remove(op[0]._id)
#        except ValueError:
#            pass
#        print "Processing: ", row
#        if op[1]:
#            print "Adding: ", op[0]
#################################
    
    if len(existing_ops):
        sync_log += ["Deleting: "]
    for existing_op in existing_ops:
        op = Operator.objects.get(_id=existing_op)
        op.delete()
        sync_log += [op.__str__()]
    conn.close()
    sync_log += ["Operators were successfully synced."]
    return 1, sync_log