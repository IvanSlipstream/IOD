import constants as C
from django.conf import settings
from datetime import datetime


class MenuItem():
    def __init__(self, name, ref, allowed_for=["managers", "tech team"]):
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
