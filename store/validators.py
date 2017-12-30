from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .username_blacklist import username_blacklist

def validate_username(value):
    if value in username_blacklist:
        raise ValidationError(
            _('%(value)s is not a valid username'),
            params={'value': value},
        )