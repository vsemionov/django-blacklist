# Django Blacklist

Blacklist users and hosts in Django. Automatically blacklist rate-limited clients.


## Overview

`Django Blacklist` allows you to block specific users and IP addresses/networks from accessing your application.
Clients can be blocked manually from the admin interface, or automatically after exceeding a request rate limit.
Each blacklist rule is applied for a specific duration.
The blacklist is very scalable and is applied without noticeable overhead for large numbers of rules.


## Installation

To install the package, run:
```shell
$ pip install django-blacklist
```

Add the `blacklist` application to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'blacklist'
]
```

Add the `BlacklistMiddleware` middleware after `AuthenticationMiddleware`:
```python
MIDDLEWARE = [
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'blacklist.middleware.BlacklistMiddleware',
    ...
]
```

Apply the blacklist database migrations:
```shell
$ python manage.py migrate blacklist
```


## Usage

You can manage the blacklist rules from the admin.
Changes take effect after a configurable time, or when the server is restarted.
A rule can target a user or an IP address.
You can also target IP networks (ranges) by specifying the optional `prefixlen` field (number of network prefix bits).
Each rule has a specific duration. After that time interval passes, the rule expires.
When a request is blocked due to a matching rule:
* Status 400 (bad request) is returned.
* An error template is rendered.
  You can specify a custom one (see `Settings` below), or use the one for status 400.
* A message is logged
  (warning from logger `blacklist.middleware` for custom templates, or error from logger `django.security` otherwise).

### Removing Expired Rules

Expired rules are not automatically removed from the database.
They can be cleaned up with the included management command `trim_blacklist`:
```shell
$ python manage.py trim_blacklist [-c <created_days>] [-e <expired_days>]
```
The options `-c` and `-e` specify the minimum ages of creation and expiry, respectively.


## Automatic Blacklisting

Clients can be blacklisted automatically, after exceeding a specified request rate limit.
This feature requires [django-ratelimit](https://github.com/jsocol/django-ratelimit).

First, rate-limit a view by applying the `@ratelimit` decorator. Make sure to set `block=False`.
Then, blacklist rate-limited clients by adding the `@blacklist_ratelimited` decorator. Specify the blacklist duration.
For example:
```python
from datetime import timedelta
from django_ratelimit.decorators import ratelimit
from blacklist.ratelimit import blacklist_ratelimited

@ratelimit(key='user_or_ip', rate='50/m', block=False)
@blacklist_ratelimited(timedelta(minutes=30))
def index(request):
    ...
```

Automatic rules take effect immediately.
If the request comes from an authenticated user, the rule will target that user.
Otherwise, it will target their IP address.

`@blacklist_ratelimited` accepts two arguments: `(duration, block=True)`.
* `duration` can be a `timedelta` object, or a tuple of two separate durations
(for user-based and IP-based rules).
* `block` specifies if the request should be blocked immediately, or passed to the view.

Automatic rules will have a comment that contains the ID of the request, which triggered the creation of the rule,
and the "request line".
The request ID is added only if available. Django does not generate request IDs.
For that purpose, you can install [django-log-request-id](https://github.com/dabapps/django-log-request-id).


## Proxies and Client Addresses

By default, the client IP address is taken from the `REMOTE_ADDR` value of `request.META`.
If your application server is behind one or more reverse proxies,
this will usually be the address of the nearest proxy, and not the actual client address.
To properly blacklist clients by IP address,
you can configure `Django Blacklist` to use addresses from another source (see `Settings` below).

To actually obtain the proxied client addresses,
you can use [django-ipware](https://github.com/un33k/django-ipware).
In this case, you can configure `Django Blacklist` to obtain client addresses from your function,
which in turn calls `django-ipware` for the actual logic.

Alternatively, you can set `REMOTE_ADDR` from the `X-Forwarded-For` header in middleware,
installed before `Django Blacklist`.
However, keep in mind that this header can be forged to bypass the rate limits.
To counter that, you can use the last address in that header (which should be set by your trusted reverse proxy).
If you are behind two proxies, use the second to last address, and so on.


## Settings

* `BLACKLIST_ENABLE` - whether blacklisted clients should be blocked,
  and rate-limited clients should be blacklisted; default: `True`
* `BLACKLIST_RELOAD_PERIOD` - how often to reload the blacklist, in seconds; default: `60`
* `BLACKLIST_RATELIMITED_ENABLE` - whether rate-limited clients should be automatically blacklisted;
  requires `BLACKLIST_ENABLE`; default: `True`
* `BLACKLIST_TEMPLATE` - name of a custom error template to render to blocked clients;
  its context will contain `request` and `exception`;
  set to `None` to use the template for status 400; default: `None`
* `BLACKLIST_LOGGING_ENABLE` - whether blocked requests should be logged
  (honored only if a custom error template is configured); default: `True`
* `BLACKLIST_ADDRESS_SOURCE` - the source of client addresses; can be a key in `request.META`,
  a callable that receives the request object, or the dotted string path to such a callable;
  default: `'REMOTE_ADDR'`
