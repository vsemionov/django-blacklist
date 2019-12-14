import logging
import ipaddress
from functools import wraps

from django.conf import settings

from ratelimit.exceptions import Ratelimited

from .models import Rule
from .middleware import _add_rule as _middleware_add_rule


logger = logging.getLogger(__name__)


def blacklist_ratelimited(duration, block=True):
    def decorator(fn):
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            if request.limited:
                if getattr(settings, 'BLACKLIST_ENABLE', True) \
                        and getattr(settings, 'BLACKLIST_RATELIMITED_ENABLE', True):
                    if user_duration and request.user.is_authenticated:
                        _create_user_rule(request, user_duration)

                    elif ip_duration:
                        _create_ip_rule(request, ip_duration)

                    else:
                        logger.warning('Unable to blacklist ratelimited client.')

                if block:
                    raise Ratelimited()

            return fn(request, *args, **kwargs)

        return wrapper

    if isinstance(duration, tuple):
        user_duration, ip_duration = duration
    else:
        user_duration = ip_duration = duration

    assert user_duration or ip_duration

    return decorator


def _create_user_rule(request, duration):
    user = request.user
    comments = _create_comments(request)
    rule = Rule(user=user, duration=duration, comments=comments)
    _add_rule(rule)


def _create_ip_rule(request, duration):
    addr = request.META['REMOTE_ADDR']
    ip = ipaddress.ip_address(addr)
    comments = _create_comments(request)
    rule = Rule(address=ip.compressed, duration=duration, comments=comments)
    _add_rule(rule)


def _create_comments(request):
    request_id = getattr(request, 'id', '')
    comments = 'Automatically blacklisted ratelimited client.\n' \
        f'Request ID: {request_id}\n' \
        f'Request line: {request.method} {request.get_full_path()}\n'
    return comments


def _add_rule(rule):
    rule.save()
    _middleware_add_rule(rule)
