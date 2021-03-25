from django.http import JsonResponse
from django.shortcuts import render
from email_simulation.forms import *
from email_simulation.models import *
from sbam_app.views import disable_form
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import F
from datetime import datetime


def sim_email_creation(request):
    if request.method == 'POST':
        new_email_form = PhishingSimulationCreationForm(request.POST, request.FILES)
        print(new_email_form.errors)
        print(new_email_form.is_valid())
        if new_email_form.is_valid():
            msg, content = handle_uploaded_file(request.FILES['email_file'])

            #TODO get the encrypted link from the environment variables
            if content.find('https://rb.gy/92erwn') == -1:
                return render(request, 'sim_email_creation.html', {
                    'mode': 'error',
                    'email_creation_form': PhishingSimulationCreationForm(),
                    'message': 'Please insert the provided url somewhere inside your email'
                })
            else:
                new_email = SimEmail(is_active=True,
                                     title=new_email_form.cleaned_data['title'],
                                     subject=new_email_form.cleaned_data['email_subject'],
                                    content=content)

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
    print('edw')
    success, content = handle_uploaded_file(request.FILES['email_file'])
    # https://developer.mozilla.org/en-US/docs/Web/API/FormData/Using_FormData_Objects
    return JsonResponse({'success': success, 'msg': content}, status=200)


def sim_endpoint(request):
    if 'ass' in request.GET:
        print(request.GET['ass'])
        print(request.GET['em'])
        email_ass = EmailAssignment.objects.filter(assignment_id=request.GET['ass'], email_id=request.GET['ass'])
        if not email_ass.exists():
            sim_assignment = EmailAssignment(assignment_id=request.GET['ass'], email_id=request.GET['em'])
            sim_assignment.answer = True
            sim_assignment.save()
            campaign = sbam_models.Campaign.objects.get(assignment=request.GET['ass'])
            assignee = sbam_models.User.objects.get(assignment=request.GET['ass'])
            assignment_result = sbam_models.AssignmentResult(assignment=sim_assignment.assignment,
                                                             score=0, answer_time=datetime.now())

            assignment_result.save()
            print(assignee)
            print(assignment_result)
            return render(request, 'esim_answer.html', {'user': assignee,
                                                        'campaign': campaign})
        else:
            JsonResponse({'success': True, 'msg': 'content'}, status=200)
    else:
        email = SimEmail.objects.get(pk=request.GET['em'])
        return render(request, 'sim_email_test_preview.html', {'email': email})


def handle_uploaded_file(f):
    email_content = ''
    success = ''
    try:
        for chunk in f.chunks():
            email_content += chunk.decode('utf-8')
        success = 'True'
    except:
        email_content += 'Could not load email'
        success = 'False'
    return success, email_content
