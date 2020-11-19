from django import forms
from django.contrib import admin
from ckeditor.widgets import CKEditorWidget

from phishing_quiz.models import PhishingEmail

class PhishingEmailAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = PhishingEmail
        fields = '__all__'

class PhishingEmailAdmin(admin.ModelAdmin):
    form = PhishingEmailAdminForm

admin.site.register(PhishingEmail, PhishingEmailAdmin)