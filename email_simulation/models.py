from django.db import models
from django.utils.translation import gettext_lazy as _
from sbam_app import models as sbam_models

# Create your models here.


class SimEmail(models.Model):
    title = models.CharField(_('title'), max_length=100, help_text=_('Campaign title'))
    is_active = models.BooleanField(default=True)
    content = models.TextField(help_text=_('Email content'), default='')


class EmailAssignment(models.Model):
    email = models.ForeignKey(
        SimEmail,
        verbose_name=_('simulation_email'),
        on_delete=models.PROTECT,
        help_text=_('The email that is send for simulation')
    )
    assignment = models.ForeignKey(
        sbam_models.TestAssignment,
        verbose_name=_('simulation_assignment'),
        on_delete=models.PROTECT,
        help_text=_('The assigment the simulation belongs')
    )

