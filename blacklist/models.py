import ipaddress
from datetime import timedelta

from django.db import models
from django.core import validators
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.conf import settings


class Rule(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)

    address = models.GenericIPAddressField(null=True, blank=True)
    prefixlen = models.PositiveIntegerField(null=True, blank=True,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(128)])

    duration = models.DurationField(validators=[validators.MinValueValidator(timedelta(0))])

    comments = models.TextField(max_length=2048, blank=True)

    def __str__(self):
        return str(self.id)

    def get_network(self):
        addr = self.address

        if addr:
            if self.prefixlen is not None:
                addr += f'/{self.prefixlen}'
            return ipaddress.ip_network(addr, strict=False)

        else:
            return None

    def get_expires(self):
        return self.created + self.duration

    def is_active(self):
        return now() < self.get_expires()

    def clean(self):
        if not self.address:
            # blank input produces empty string
            self.address = None

        if self.address is None and self.prefixlen is not None:
            raise ValidationError('Prefixlen without address.')

        try:
            self.get_network()

        except ValueError as ve:
            raise ValidationError(str(ve))

        if self.user is None and self.address is None:
            raise ValidationError('Neither user nor address provided.')

        if self.user is not None and self.address is not None:
            raise ValidationError('Both user and address provided.')
