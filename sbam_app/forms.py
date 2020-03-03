from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django.forms import *
from django.utils.safestring import mark_safe

from sbam_app.models import *


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password', 'is_superuser', 'groups')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

        self.fields['password'].widget = PasswordInput(render_value=True)
        self.fields['password'].disabled = True
        self.fields['password'].initial = 'dummy'

        self.general_info_helper = FormHelper()
        self.general_info_helper.form_tag = False;
        self.general_info_helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-3'),
                Column('last_name', css_class='col-md-4'),
                Column(AppendedText('email', mark_safe('<i class="fas fa-envelope"></i>')), css_class='col-md-5')
            )
        )

        self.credentials_helper = FormHelper()
        self.credentials_helper.form_tag = False;
        self.credentials_helper.layout = Layout(
            Row(
                Column(AppendedText('username', mark_safe('<i class="fas fa-user"></i>')), attrs='',
                       css_class='col-md-6'),
                Column(AppendedText('password', mark_safe('<i class="fas fa-lock"></i>'), id='password'),
                       css_class='col-md-6'
                       )
            )
        )

        self.new_user_helper = FormHelper()
        self.new_user_helper.form_tag = False;
        self.new_user_helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-5'),
                Column('last_name', css_class='col-md-7')
            ),
            Row(
                Column(AppendedText('email', mark_safe('<i class="fas fa-envelope"></i>')), css_class='col-md-12')
            ),
            Row(
                Column(AppendedText('username', mark_safe('<i class="fas fa-user"></i>')), attrs='',
                       css_class='col-md-12')
            )
        )


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.general_info_helper = FormHelper()
        self.general_info_helper.form_tag = False;
        self.general_info_helper.layout = Layout(
            Row(
                Column('employee_id', css_class='col-md-4'),
                Column(AppendedText('birth_date', mark_safe('<i class="fas fa-calendar-alt"></i>'),
                                    css_class='datepicker'), css_class='col-md-4'),
                Column('gender', css_class='col-md-4')
            ),
            Row(
                Column('notes', css_class='col-md-12')
            )
        )

        self.contact_details_helper = FormHelper()
        self.contact_details_helper.form_tag = False;
        self.contact_details_helper.layout = Layout(
            Row(
                Column('address', css_class='col-md-9'),
                Column('telephone', css_class='col-md-3')
            )
        )

        self.organizational_info_helper = FormHelper()
        self.organizational_info_helper.form_tag = False;
        self.organizational_info_helper.layout = Layout(
            Row(
                Column('job_title', css_class='col-md-6'),
                Column('department', css_class='col-md-6'),
            ),
            Row(
                Column('company', css_class='col-md-6')
            )
        )
