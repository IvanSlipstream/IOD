# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime

from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.defaults import permission_denied, page_not_found
from django.http import HttpResponse

from RFC import track
from RFC.models import *
import tools
import sync
import details
import constants
import logger
import override
import _docx

@login_required
def add_rfc(request, rfc_to_edit=None):
    c = tools.default_context(request)
    if not tools.has_access(request, "managers"):
        return permission_denied(request)
    new_rfc = None
    c['title'] = "Add RFC"
    c['new_added'] = True
    c['oper_our'] = Operator.objects.filter(isDirect=True).order_by('fineName')
    c['oper_foreign'] = Operator.objects.all().order_by('fineName')
    # c['priorities'] = dict(ChangeRequest.PRIO_CHOICE)
    if request.method == "POST":
        _author = request.user
        _dt = tools.date_parse_input(request.POST['rfc_date']).date()
        if _dt < date.today():
            return permission_denied(request)
        _comments = request.POST['comments']
        _prio = request.POST['prio']
        _peer_hub = request.POST['peer_hub']
        _oper_our = request.POST['oper_our']
        _oper_foreign = request.POST['oper_foreign']
        _towards = request.POST['towards']
        _backwards = request.POST['backwards']
        new_rfc = ChangeRequest(
            author=_author,
            dt=_dt,
            comments=_comments,
            prio=_prio,
            peer_hub=_peer_hub,
            oper_our=Operator.objects.get(_id=int(_oper_our)),
            oper_foreign=Operator.objects.get(_id=int(_oper_foreign)),
            direction=1 * int(_towards) + 2 * int(_backwards),
        )
        new_rfc.save()
        logger.log_action(user=_author, action=logger.ACTION_ADD_RFC, rfc=new_rfc)
        c['saved'] = "Saved: " + new_rfc.__str__()
        c['link'] = new_rfc.id
        c['new_added'] = False
        c['peer_hub'] = _peer_hub
        c['oper_our_previous'] = Operator.objects.get(_id=int(_oper_our))
        c['oper_foreign_previous'] = Operator.objects.get(_id=int(_oper_foreign))
        c['towards'] = int(_towards)
        c['backwards'] = int(_backwards)
        c['override'] = override.find_overriden(new_rfc)
    if rfc_to_edit is not None:
        # then delete old RFC and create another
        c['title'] = "Edit RFC"
        c['rfc_date'] = rfc_to_edit.dt
        c['oper_our_previous'] = rfc_to_edit.oper_our
        c['oper_foreign_previous'] = rfc_to_edit.oper_foreign
        c['peer_hub'] = rfc_to_edit.peer_hub
        c['comments'] = rfc_to_edit.comments
        c['backwards'] = rfc_to_edit.direction // 2
        c['towards'] = rfc_to_edit.direction % 2
        c['new_added'] = False
        rfc_to_edit.delete()
        if isinstance(new_rfc, ChangeRequest):
            return redirect('/detail/' + str(new_rfc.id))
    return render_to_response('addRFC.html', c)


@login_required
def list_rfc(request):
    c = tools.default_context(request)
    c['title'] = "View RFCs"
    yesterday = date.today() - timedelta(days=1)
    c['start_date'] = yesterday
    c['end_date'] = date.today()
    c['include_completed_route'] = False
    c['include_new'] = True
    c['rfc_list'] = ChangeRequest.objects.all().order_by('cur_state', '-dt')
    result_set = c['rfc_list']
    rfc_states = ['include_new', 'include_implemented', 'include_completed', 'include_untrackable',
                  'include_overriden', 'include_rejected']
    if request.method == 'POST':
        _filter_author = request.POST['filter_author']
        _filter_oper_our = request.POST['filter_oper_our']
        _filter_oper_foreign = request.POST['filter_oper_foreign']
        _filter_peer_hub = request.POST['filter_peer_hub']
        _filter_start_date = tools.date_parse_input(request.POST['start_date']).date()
        _filter_end_date = tools.date_parse_input(request.POST['end_date']).date()
        _filter_states = [bool(request.POST.get(state, False)) for state in rfc_states]
        result_set = result_set.filter(cur_state__in=[i for i in range(len(_filter_states)) if _filter_states[i]])
        if request.POST.get('use_date_filter', False):
            result_set = result_set.filter(
                Q(dt__gte=_filter_start_date) & Q(dt__lte=_filter_end_date)
            )
        if _filter_author != "":
            result_set = result_set.filter(
                Q(author__username__icontains=_filter_author) |
                Q(author__last_name__icontains=_filter_author) |
                Q(author__first_name__icontains=_filter_author)
            )
        if _filter_oper_our != "":
            result_set = result_set.filter(
                Q(oper_our__fineName__icontains=_filter_oper_our) |
                Q(oper_our__e212__icontains=_filter_oper_our)
            )
        if _filter_oper_foreign != "":
            result_set = result_set.filter(
                Q(oper_foreign__fineName__icontains=_filter_oper_foreign) |
                Q(oper_foreign__e212__icontains=_filter_oper_foreign)
            )
        if _filter_peer_hub != "":
            result_set = result_set.filter(peer_hub__icontains=_filter_peer_hub)
        c['filter_author'] = _filter_author
        c['filter_oper_our'] = _filter_oper_our
        c['filter_oper_foreign'] = _filter_oper_foreign
        c['filter_peer_hub'] = _filter_peer_hub
        c['start_date'] = _filter_start_date
        c['end_date'] = _filter_end_date
        c['use_date_filter'] = bool(request.POST.get('use_date_filter', False))
        for i in range(len(rfc_states)):
            c[rfc_states[i]] = _filter_states[i]
    else:
        result_set = result_set.filter(cur_state__in=[0])
    c['rfc_list'] = result_set
    if not len(result_set):
        c['no_rfcs'] = True
    return render_to_response('listRFC.html', c)

def user_login(request):
    c = tools.default_context(request)
    if request.user.is_authenticated():
        c['title'] = "Main Page"
    else:
        c['title'] = "Log In"
    if request.method == "POST":
        _user = request.POST['user']
        _pass = request.POST['pass']
        user = authenticate(username=_user, password=_pass)
        if user is not None:
            if user.is_active:
                login(request, user)
                logger.log_action(user=user, action=logger.ACTION_LOG_IN)
                return redirect(request.GET.get("next", "/"))
            else:
                c['warning'] = "User is inactive."
        else:
            c['warning'] = "The username or password were incorrect."
#    from django.conf import settings
#    print settings.DATABASES
    return render_to_response('login.html', c)


@login_required
def user_logout(request):
    c = tools.default_context(request)
    c['title'] = "Log Out"
    logger.log_action(user=request.user, action=logger.ACTION_LOG_OUT)
    logout(request)
    c['warning'] = "You were logged out."
    c['is_user'] = False
    return render_to_response('logout.html', c)


@login_required
def user_profile(request):
    c = tools.default_context(request)
    c['title'] = "User Profile"
    user = request.user
    try:
        user_meta = UserMeta.objects.get(user_reference=user)
    except UserMeta.DoesNotExist:
        print "Creating metadata for user %s" % user
        user_meta = UserMeta(
            user_reference=user,
            phone_work='600',
            phone_mob='No mobile phone'
        )
        user_meta.save()
    if request.method == "POST":
        _position = request.POST['position']
        _phone_work = request.POST['phone_work']
        _phone_mob = request.POST['phone_mob']
        _first_name = request.POST['first_name']
        _last_name = request.POST['last_name']
        _pass = request.POST['password']
        _confirm_pass = request.POST['confirm_password']
        if _pass == _confirm_pass and _pass != "":
            user.set_password(_pass)
        elif _pass != _confirm_pass:
            c['warning'] = "Passwords do not match!"
        user_meta.position = _position
        user_meta.user_reference = user
        user_meta.phone_work = _phone_work
        user_meta.phone_mob = _phone_mob
        user_meta.save()
        user.first_name = _first_name
        user.last_name = _last_name
        user.save()
    c['position'] = user_meta.position
    c['phone_work'] = user_meta.phone_work
    c['phone_mob'] = user_meta.phone_mob
    c['first_name'] = user.first_name
    c['last_name'] = user.last_name
    return render_to_response('profile.html', c)


@login_required
def oper_sync(request):
    c = tools.default_context(request)
    if not tools.has_access(request, "tech team"):
        return permission_denied(request)
    c['title'] = "Manage Operators"
    if request.method == "POST":
        c['result'] = sync.sync()[1]
        logger.log_action(request.user, action=logger.ACTION_SYNC_OPERATORS)
    c['opers'] = Operator.objects.all()
    return render_to_response('sync.html', c)


@login_required
def rfc_override(request, id):
    try:
        rfc = ChangeRequest.objects.get(id=id)
        rfc.cur_state = 4
        rfc.save(force_update=True)
        logger.log_action(request.user, rfc, logger.ACTION_OVERRIDE)
        return HttpResponse(status=200)
    except ChangeRequest.DoesNotExist:
        return HttpResponse(status=500)


@login_required
def rfc_details(request, id):
    c = tools.default_context(request)
    c['req_id'] = id
    c['title'] = "RFC#" + id
    _rfc = ChangeRequest.objects.get(id=id)
    author = _rfc.author
    c['author'] = UserMeta.objects.get(user_reference=author)
    c['rfc'] = _rfc
    c['mail_link'] = constants.RFC_NOTIFICATION_MAIL_LINK.format(oper_our=_rfc.oper_our.fineName)
    query_result = details.stat(_rfc.dt.strftime('%Y-%m-%d'),
                                _rfc.oper_our._id,
                                _rfc.oper_foreign._id)
    c['is_data'] = query_result[0]
    c['trackers'] = Tracker.objects.filter(rfc=_rfc)
    for tracker in c['trackers']:
        if track.is_tracker_fulfilled_immediate(tracker):
            tracker.fulfilled = True
            tracker.save()
    if query_result[0]:
        c['table_data'] = query_result[1]
        counts = [row['cnt'] for row in query_result[1]]
        if len(counts) > 0:
            c['max'] = max(counts)
    else:
        c['warning'] = query_result[1]
    if request.method == "POST":
        pass
    return render_to_response('detailRFC.html', c)

@login_required
def update_tracker_comment_rfc(request, id):
    try:
        print "Request", request.POST
        new_comment = request.POST.dict().keys()[0]
        rfc_tracker_commment = ChangeRequest.objects.get(id=int(id))
        rfc_tracker_commment.tracker_comment = new_comment
        rfc_tracker_commment.save()
        return HttpResponse(status=200)
    except BaseException as e:
        print e.message
        return HttpResponse(status=500)

@login_required
def tracker_add(request, id):
    c = tools.default_context(request)
    tracker = Tracker()
    rfc = ChangeRequest.objects.get(id=id)
    c['rfc'] = rfc
    c['title'] =  "Add Tracker"
    if request.method == "POST":
        _direction = request.POST.get('direction', 1)
        _amount = request.POST.get('amount', 0)
        _any_route = request.POST.get('any_route', False)
        _route = request.POST.get('route', None)
        try:
            tracker.rfc = rfc
            tracker.direction = int(_direction)
            tracker.count = int(_amount)
            if bool(_any_route):
                tracker.route = None
            else:
                tracker.route = _route
            tracker.save()
            logger.log_action(request.user, rfc, logger.ACTION_ADD_TRACKER)
            return redirect('/detail/%s/' % id)
        except ValueError:
            for key in request.POST.dict().keys():
                c[key] = request.POST.get(key)
                c['error_code'] = 1
    return render_to_response("add_tracker.html", c)

@login_required
def tracker_unbind(request, id):
    tracker = Tracker.objects.get(id=id)
    rfc_id = str(tracker.rfc.id)
    tracker.delete()
    logger.log_action(request.user, tracker.rfc, logger.ACTION_REMOVE_TRACKER)
    return redirect('/detail/' + rfc_id + '/')

@login_required
def untrack_rfc(request, id):
    if not tools.has_access(request, "tech team"):
        return permission_denied(request)
    rfc = ChangeRequest.objects.get(id=id)
    trackers = Tracker.objects.filter(rfc=rfc)
    rfc.cur_state = 3
    rfc.save(force_update=True)
    for tracker in trackers:
        tracker.delete()
    logger.log_action(request.user, rfc, logger.ACTION_MARK_UNTRACKABLE)
    return redirect('/detail/' + id + '/')

@login_required
def rfc_reject(request, id):
    if not tools.has_access(request, "tech team"):
        return permission_denied(request)
    rfc = ChangeRequest.objects.get(id=id)
    rfc.cur_state = 5
    rfc.save()
    logger.log_action(request.user, rfc, logger.ACTION_REJECT)
    return redirect('/detail/' + id + '/')

@login_required
def paper_rfc(request, id):
    if not tools.has_access(request, "managers"):
        return permission_denied(request)
    return _docx.inflate_docx(int(id))


@login_required
def combined_rfc(request, id):
    if request.method == "POST":
        if not tools.has_access(request, "managers"):
            return permission_denied(request)
        chosen_rfcs = [int(k[1:]) for k in request.POST.keys() if k[0] == "c" and request.POST[k]]
        return _docx.inflate_docx(int(id), chosen_rfcs=chosen_rfcs)
    else:
        c = tools.default_context(request)
        c['title'] = "Include to combined RFC"
        rfc_base = ChangeRequest.objects.get(id=id)
        rfcs = ChangeRequest.objects.filter(dt__gte=rfc_base.dt).filter(oper_our=rfc_base.oper_our)
        c['rfcs'] = rfcs
        return render_to_response("combinedRFC.html", c)


#@login_required
def rfc_test(request):
    chosen_rfcs = [61, 62, 63]
    return _docx.inflate_docx(61)


@login_required
def rfc_confirm(request, id):
    if not tools.has_access(request, ["managers", "tech team"]):
        return permission_denied(request)
    _rfc = ChangeRequest.objects.get(id=id)
    _rfc.cur_state = 2
    logger.log_action(user=request.user, action=logger.ACTION_CONFIRM_TRAFFIC, rfc=_rfc)
    _rfc.save()
    return redirect('/detail/' + id + '/')


@login_required
def rfc_apply(request, id):
    if not tools.has_access(request, "tech team"):
        return permission_denied(request)
    _rfc = ChangeRequest.objects.get(id=id)
    if _rfc.cur_state == 0:
        _rfc.cur_state = 1
        logger.log_action(user=request.user, action=logger.ACTION_CONFIRM_ROUTE, rfc=_rfc)
    _rfc.save()
    return redirect('/detail/' + id + '/')


@login_required
def rfc_delete(request, id):
    try:
        _rfc = ChangeRequest.objects.get(id=id)
    except ChangeRequest.DoesNotExist:
        return page_not_found(request)
    if not (tools.has_access(request, ["managers"]) and _rfc.cur_state == 0):
        return permission_denied(request)
    logger.log_action(user=request.user, action=logger.ACTION_REMOVE_RFC, rfc=_rfc)
    _rfc.delete()
    return redirect('/list/')


@login_required
def rfc_edit(request, id):
    c = tools.default_context(request)
    c['title'] = "Edit RFC"
    try:
        _rfc = ChangeRequest.objects.get(id=id)
        _rfc_cur_state = _rfc.cur_state
    except ChangeRequest.DoesNotExist:
        _rfc = None
        _rfc_cur_state = 0
    if not (tools.has_access(request, ["managers"]) and _rfc_cur_state == 0):
        return permission_denied(request)
    return add_rfc(request, _rfc)