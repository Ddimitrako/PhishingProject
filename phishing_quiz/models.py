from django.db import models
from django.utils.translation import gettext_lazy as _
from sbam_app import models as sbam_models


class PhishingEmail(models.Model):
    content = models.TextField(help_text=_('Email content'), default='')
    is_phishing = models.BooleanField()
    sender_email = models.CharField(_('sender_email'), max_length=100, help_text=_('Sender\'s Email'))
    sender_display_name = models.CharField(_('sender_display_name'), max_length=100, help_text=_('Sender\'s Name'))
    is_active = models.BooleanField(default=True)


class PhishingEmailAssignmentAnswer(models.Model):
    email = models.ForeignKey(
        PhishingEmail,
        verbose_name=_('phishing_email'),
        on_delete=models.PROTECT,
        help_text=_('The email that is referred')

    )
    user_answer = models.BooleanField()
    assignment = models.ForeignKey(
        sbam_models.Assignment,
        on_delete=models.PROTECT,
        help_text=_('The assignment this answer belongs to')
    )


class PhishingEmailQuizScore(models.Model):
    assignment = models.ForeignKey(
        sbam_models.Assignment,
        on_delete=models.PROTECT,
        help_text=_('The assignment this answer belongs to')
    )
    score = models.FloatField(_('score'), help_text=_('Achieved score in phishing quiz'))

