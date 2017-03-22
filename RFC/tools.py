import constants as C
from django.conf import settings
from datetime import datetime


class MenuItem():
    def __init__(self, name, ref, allowed_for=None):
        if allowed_for is None:
            allowed_for = ["managers", "tech team"]
        self.name = name
        self.ref = ref
        self.allowed_for = allowed_for

    def allowed_for_user(self, user):
        for group in self.allowed_for:
            if len(user.groups.filter(name=group)) > 0:
                return True
        return False


MENU_ITEMS = [
    MenuItem("Create RFC", "/add/", ["managers"]),
    MenuItem("List RFC", "/list/"),
    MenuItem("Operators", "/sync/", ["tech team"]),
    MenuItem("Admin site", "/admin/"),
]


def default_context(request):
    c = {}
    c['items'] = [menu_item for menu_item in MENU_ITEMS if menu_item.allowed_for_user(request.user)]
    c['sup_mail'] = C.SUPPORT_MAIL
    c['sup_login'] = C.SUPPORT_LOGIN
    c['version'] = C.PROJECT_VERSION
    if request.user.is_authenticated():
        c['is_user'] = True
        c['username'] = request.user
    else:
        c['is_user'] = False
    return c


def synchro_opers():
    pass


def has_access(request, permissions):
    if isinstance(permissions, list):
        for perm in permissions:
            if len(request.user.groups.filter(name=perm)) > 0:
                return True
        return False
    else:
        return len(request.user.groups.filter(name=permissions)) > 0


def date_parse_input(date_str):
    for date_format in settings.DATE_INPUT_FORMATS:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            pass

def adopt(in_array):
    # combining array of ints into human-readable enumeration
    # like "20, 25-29, 31"
    in_array.sort()
    tuple_result = [(in_array[0], in_array[0])]
    str_result = ""
    if len(in_array)==1:
        return str(in_array[0])
    for i in range(1,len(in_array)):
        if in_array[i-1]+1==in_array[i]:
            tuple_result[-1] = (tuple_result[-1][0], in_array[i])
        else:
            tuple_result+=[(in_array[i], in_array[i])]
    for pair in tuple_result:
        if pair[0]==pair[1]:
            str_result+=pair[0].__str__()+", "
        else:
            str_result+=pair[0].__str__()+"-"+pair[1].__str__()+", "
    return str_result[:-2]

