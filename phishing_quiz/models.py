from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.translation import gettext_lazy as _
from sbam_app import models as sbam_models

class PhishingEmail(models.Model):
    content = RichTextUploadingField()
    is_phishing = models.BooleanField()
    sender_email = models.CharField(_('sender_email'), max_length=100, help_text=_('Sender\'s Email'))
    sender_display_name = models.CharField(_('sender_display_name'), max_length=100, help_text=_('Sender\'s Name'))
    is_active = models.BooleanField()


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


