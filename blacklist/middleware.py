import ipaddress
import threading
from typing import Optional, Set
import logging

from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render
from django.conf import settings

from .models import Rule


logger = logging.getLogger(__name__)


_blacklist: Optional[Set[Rule]] = None
_blacklist_lock = threading.Lock()


class Blacklisted(SuspiciousOperation):
    pass


def blacklist_middleware(get_response):
    def middleware(request):
        if getattr(settings, 'BLACKLIST_ENABLE', True):
            if _blacklist is None:
                _load_blacklist()

            try:
                _filter_client(request)

            except Blacklisted as exception:
                template_name = getattr(settings, 'BLACKLIST_TEMPLATE', None)

                if template_name:
                    logger.warning(exception)
                    context = {'request': request, 'exception': exception}
                    return render(request, template_name, context, status=400)

                raise

        return get_response(request)

    return middleware


def _filter_client(request):
    client_user = request.user
    client_user_id = client_user.id

    client_addr = request.META['REMOTE_ADDR']
    client_ip = ipaddress.ip_address(client_addr)

    inactive_rules = set()

    for rule in _blacklist:
        if rule.is_active():
            # no logging here, because the event will be logged either by the caller, or by django.security

            rule_user_id = rule.user_id
            if rule_user_id is not None and client_user_id == rule_user_id:
                message = 'Blacklisted client user: %s' % client_user.username
                raise Blacklisted(message)

            rule_network = rule.get_network()
            if rule_network is not None and client_ip in rule_network:
                message = 'Blacklisted client address: %s' % client_addr
                raise Blacklisted(message)

        else:
            inactive_rules.add(rule)

        if inactive_rules:
            _remove_rules(inactive_rules)


def _load_blacklist():
    global _blacklist

    with _blacklist_lock:
        _blacklist = {rule for rule in Rule.objects.all() if rule.is_active()}


def _add_rule(rule):
    global _blacklist

    with _blacklist_lock:
        _blacklist = _blacklist | {rule}


def _remove_rules(rules):
    global _blacklist

    with _blacklist_lock:
        _blacklist = _blacklist - rules
