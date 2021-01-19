from django.db import models
from django.utils.translation import gettext_lazy as _
from sbam_app import models as sbam_models

# Create your models here.


class SimEmail(models.Model):
    title = models.CharField(_('title'), max_length=100, help_text=_('Campaign title'))
    is_active = models.BooleanField(default=True)
    content = models.TextField(help_text=_('Email content'), default='')

