import ipaddress
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Union
import logging

from django.core.exceptions import SuspiciousOperation
from django.db.models import F, Max, DateTimeField
from django.utils.timezone import now
from django.shortcuts import render
from django.conf import settings

from .models import Rule


logger = logging.getLogger(__name__)


_RELOAD_PERIOD = timedelta(seconds=getattr(settings, 'BLACKLIST_RELOAD_PERIOD', 60))

_user_blacklist: Dict[int, datetime] = {}
_addr_blacklist: Dict[Optional[int], Dict[Union[ipaddress.IPv4Network, ipaddress.IPv6Network], datetime]] = {}

_loaded: Optional[datetime] = None

_blacklist_lock = threading.Lock()


class Blacklisted(SuspiciousOperation):
    pass


def blacklist_middleware(get_response):
    def middleware(request):
        if getattr(settings, 'BLACKLIST_ENABLE', True):
            current_time = now()

            if _needs_reload(current_time):
                _load_blacklist()

            try:
                _filter_client(request, current_time)

            except Blacklisted as exception:
                template_name = getattr(settings, 'BLACKLIST_TEMPLATE', None)

                if template_name:
                    if getattr(settings, 'BLACKLIST_LOGGING_ENABLE', True):
                        logger.warning(exception)

                    context = {'request': request, 'exception': exception}
                    return render(request, template_name, context, status=400)

                raise

        return get_response(request)

    return middleware


def _filter_client(request, current_time):
    user = request.user
    user_id = user.id

    addr = request.META['REMOTE_ADDR']

    # no logging here, because the event will be logged either by the caller, or by django.request

    until = _user_blacklist.get(user_id)
    if until is not None and until > current_time:
        raise Blacklisted('Blacklisted user: %s' % user.username)

    for prefixlen, blacklist in _addr_blacklist.items():
        network = Rule(address=addr, prefixlen=prefixlen).get_network()

        until = blacklist.get(network)
        if until is not None and until > current_time:
            raise Blacklisted('Blacklisted address: %s' % addr)


def _needs_reload(current_time):
    return _loaded is None or current_time >= _loaded + _RELOAD_PERIOD


def _load_blacklist():
    global _loaded, _user_blacklist, _addr_blacklist

    with _blacklist_lock:
        current_time = now()

        if _needs_reload(current_time):
            until = Max(F('created') + F('duration'), output_field=DateTimeField())
            rules = Rule.objects.values('user_id', 'address', 'prefixlen').annotate(until=until)
            rules = rules.filter(until__gt=current_time)

            user_blacklist = {}
            addr_blacklist = {}

            for rule in rules:
                user_id = rule['user_id']
                prefixlen = rule['prefixlen']
                network = Rule(address=rule['address'], prefixlen=prefixlen).get_network()
                until = rule['until']

                _add_client(user_blacklist, addr_blacklist, user_id, prefixlen, network, until)

            _user_blacklist = user_blacklist
            _addr_blacklist = addr_blacklist
            _loaded = now()


def _add_client(user_blacklist, addr_blacklist, user_id, prefixlen, network, until):
    if user_id is not None:
        current_until = user_blacklist.get(user_id)
        if current_until is None or current_until < until:
            user_blacklist[user_id] = until

    if network is not None:
        blacklist = addr_blacklist.setdefault(prefixlen, {})
        current_until = blacklist.get(network)
        if current_until is None or current_until < until:
            blacklist[network] = until


def _add_rule(rule):
    global _addr_blacklist

    with _blacklist_lock:
        user_id = rule.user_id
        prefixlen = rule.prefixlen
        network = rule.get_network()
        until = rule.get_expires()

        addr_blacklist = _addr_blacklist.copy()
        _add_client(_user_blacklist, addr_blacklist, user_id, prefixlen, network, until)
        _addr_blacklist = addr_blacklist
