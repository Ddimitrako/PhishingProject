from django.shortcuts import render
from email_simulation.forms import *
from email_simulation.models import *
from phishing_quiz.views import handle_uploaded_file
from django.views.decorators.clickjacking import xframe_options_exempt


def email_creation(request):
    if request.method == 'POST':
        new_email_form = PhishingSimulationCreationForm(request.POST, request.FILES)
        print(new_email_form.errors)
        print(new_email_form.is_valid())
        if new_email_form.is_valid():

            new_email = SimEmail(is_active=True,
                                 title=new_email_form.cleaned_data['title'],
                                content=handle_uploaded_file(request.FILES['email_file'])
                                )
            new_email.save()
            return render(request, 'email_creation.html', {
                'email_creation_form': new_email_form,
                'message': 'success'
            })
        else:
            return render(request, 'email_creation.html', {
                'email_creation_form': PhishingSimulationCreationForm(),
                'message': new_email_form.errors
            })
    else:
        email_creation_form = PhishingSimulationCreationForm()
        return render(request, 'email_creation.html', {
            'email_creation_form': email_creation_form
        })

@xframe_options_exempt
def email_request(request, email_id):

    email = SimEmail.objects.get(id=email_id)
    return render(request, 'email_template.html', {'email': email})