from datetime import date
from RFC.models import *
test_oper_A = Operators(_id=12, fineName="Ucell test", isDirect=True)
test_oper_B.save()
test_oper_A = Operators(_id=15, fineName="Swisscom test", isDirect=False)
test_oper_B.save()
test_user = Users(login="me", firstName="Ivan", lastName="Slipstream", phone="666", email="ik@gmsu.ua")
test_user.save()
test_rfc = ChangeRequest(author=test_user, dt=date.today(), comments="hello", prio=1, peer_hub="BICS", oper_our=test_oper_A, oper_foreign=test_oper_B)