from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django.forms import *
from django.utils.safestring import mark_safe

from sbam_app.models import *


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Row(
                Column('employee_id', css_class='col-4'),
                Column(AppendedText('birth_date', mark_safe('<i class="fas fa-calendar-alt"></i>'),
                                    css_class='datepicker'), css_class='col-4'),
                Column('gender', css_class='col-4')
            ),
            Accordion(
                AccordionGroup(
                    'Contact Details',
                    Row(
                        Column('address', css_class='col-9'),
                        Column('telephone', css_class='col-3')
                    ),
                    active=False
                ),
                AccordionGroup(
                    'Organizational Info',
                    Row(
                        Column('job_title', css_class='col-6'),
                        Column('department', css_class='col-6'),
                    ),
                    Row(
                        Column('company', css_class='col-6')
                    )
                ),
            ),
        )
