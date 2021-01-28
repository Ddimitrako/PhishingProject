from django.http import JsonResponse
from django.shortcuts import render
from email_simulation.forms import *
from email_simulation.models import *
from sbam_app.views import disable_form
from django.views.decorators.clickjacking import xframe_options_exempt


def sim_email_creation(request):
    if request.method == 'POST':
        new_email_form = PhishingSimulationCreationForm(request.POST, request.FILES)
        print(new_email_form.errors)
        print(new_email_form.is_valid())
        if new_email_form.is_valid():

            new_email = SimEmail(is_active=True,
                                 title=new_email_form.cleaned_data['title'],
                                 subject=new_email_form.cleaned_data['email_subject'],
                                content=handle_uploaded_file(request.FILES['email_file'])
                                )
            new_email.save()
            new_form = PhishingSimulationCreationForm(initial={'title': new_email.title,
                                                               'email_subject': new_email.subject,
                                                               'email_file': request.FILES['email_file']})
            print(new_form)
            disable_form(new_form)
            return render(request, 'sim_email_creation.html', {
                'mode': 'submitted',
                'email': new_email.id,
                'email_creation_form': new_form,
                'message': 'success'
            })
        else:
            return render(request, 'sim_email_creation.html', {
                'mode': 'error',
                'email_creation_form': PhishingSimulationCreationForm(),
                'message': new_email_form.errors
            })
    else:
        email_creation_form = PhishingSimulationCreationForm()
        return render(request, 'sim_email_creation.html', {
            'mode': 'rendered',
            'email_creation_form': email_creation_form
        })


@xframe_options_exempt
def sim_email_request(request, email_id):

    email = SimEmail.objects.get(id=email_id)
    return render(request, 'email_template.html', {'email': email})


def email_preview(request):
    # print(request.POST['email_file'])
    # for a in request.POST['email_file']:
    #     print(a)
    print(request.FILES)

    # https://developer.mozilla.org/en-US/docs/Web/API/FormData/Using_FormData_Objects
    return JsonResponse({'success': 'True', 'msg': handle_uploaded_file(request.FILES['email_file'])}, status=200)


def sim_endpoint(request):
    print(request.GET['ass'])
    print(request.GET['em'])
    # print(ass_id, email_id)
    return


def handle_uploaded_file(f):
    email_content = ''
    for chunk in f.chunks():
        email_content += chunk.decode('utf-8')
    return email_content
