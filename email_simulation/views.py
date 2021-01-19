from django.shortcuts import render
from email_simulation.forms import *
from email_simulation.models import *
# Create your views here.


def email_creation(request):
    if request.method == 'POST':
        new_email_form = PhishingSimulationCreationForm(request.POST, request.FILES)
        print(new_email_form.errors)
        print(new_email_form.is_valid())
        # if new_email_form.is_valid():
        #
        #     new_email = PhishingEmail(sender_email=new_email_form.cleaned_data['sender_email'],
        #                               is_phishing=new_email_form.cleaned_data['is_phishing'],
        #                               sender_display_name=new_email_form.cleaned_data['sender_display_name'],
        #                               content=handle_uploaded_file(request.FILES['email_file'])
        #                               )
        #     new_email.save()
        #     return render(request, 'email_creation.html', {
        #         'email_creation_form': new_email_form,
        #         'message': 'success'
        #     })
        # else:
        #     return render(request, 'email_creation.html', {
        #         'email_creation_form': PhishingSimulationCreationForm(),
        #         'message': new_email_form.errors
        #     })
        # return redirect('/')
    else:
        email_creation_form = PhishingSimulationCreationForm()
        return render(request, 'email_creation.html', {
            'email_creation_form': email_creation_form
        })


