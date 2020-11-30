from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django import forms


class PhishingEmailCreationForm(forms.Form):
    # class Meta:
    #     fields = ('is_phishing', 'sender_email', 'sender_display_name', 'email_file')

    is_phishing = forms.TypedChoiceField(
        label="Is a Phishing email?",
        choices=((1, "Yes"), (0, "No")),
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        initial='1',
        required=True,
    )
    sender_email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'user@example,com'}), required=True)
    sender_display_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'John Papadopoulos'}), required=True)
    email_file = forms.FileField()

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.general_info_helper = FormHelper()
        self.general_info_helper.layout = Layout(
            Row(
                Column('sender_email', css_class='form-group col-md-4 mb-0'),
                Column('is_phishing', css_class='form-group col-md-4 offset-md-1 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('sender_display_name', css_class='form-group col-md-4 mb-0'),

                Column('email_file', css_class='form-group col-md-4 offset-md-1 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Create Email', css_class='float-right')
        )

