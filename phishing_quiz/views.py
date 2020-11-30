from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from phishing_quiz.models import *
from phishing_quiz.forms import *

from django.views.decorators.clickjacking import xframe_options_exempt
import json
from sbam_app.templatetags import custom_tags
from django.shortcuts import redirect
from datetime import datetime


# Create your views here.
def phishing_quiz(request, assignment_id):
    if request.method == 'POST':
        print(request.POST['ass_id'])

        answers = json.loads(request.POST['data'])
        emails_ids = []
        for email in answers:
            emails_ids.append(int(answers[email]['id']))

        labels = PhishingEmail.objects.filter(pk__in=emails_ids)
        test_assignment = sbam_models.TestAssignment.objects.get(pk=request.POST['ass_id'])
        correct_answers = 0
        for true_label, email in zip(labels, answers):
            new_answer = PhishingEmailAssignmentAnswer(email=true_label, user_answer=answers[email]['answer'], assignment=test_assignment)
            new_answer.save()
            if true_label.is_phishing == answers[email]['answer']:
                correct_answers += 1

        quiz_score = PhishingEmailQuizScore(assignment=test_assignment, score=correct_answers / len(labels) * 100)
        quiz_score.save()
        assignment_result = sbam_models.AssignmentResult(assignment=test_assignment,
                                                         score=correct_answers / len(labels), answer_time=datetime.now())

        assignment_result.save()
        return JsonResponse({
                             'score': correct_answers / len(labels) * 100,
                             'score_badge': custom_tags.get_badge(str(correct_answers / len(labels) * 100)),
                         })

    else:

        # na dialegeis 10 random emails otan ftiaxtei
        # Na koitaei ti exei apanthsei kai se poia exei kanei lathos etsi wste na dinetai proteraiothta se auta
        test_emails = PhishingEmail.objects.filter(is_active=True)
        assignment = sbam_models.TestAssignment.objects.get(pk=assignment_id)
        return render(request, 'phishing_quiz.html', {'emails': test_emails,
                                                      'assignment_id': assignment.id,
                                                      'progress_bar': 1 / len(test_emails) * 100})


@xframe_options_exempt
def email_request(request, email_id):

    email = PhishingEmail.objects.get(id=email_id)
    current_time = datetime.now().strftime("%H:%M")
    current_time = current_time + ' PM' if datetime.now() > datetime.now().replace(hour=12, minute=0) else current_time + ' AM'
    return render(request, 'email_template.html', {'email': email,
                                                   'time': current_time})

def email_creation(request):
    if request.method == 'POST':
        new_email_form = PhishingEmailCreationForm(request.POST, request.FILES)
        print(new_email_form.errors)
        print(new_email_form.is_valid())
        if new_email_form.is_valid():

            new_email = PhishingEmail(sender_email=new_email_form.cleaned_data['sender_email'],
                                      is_phishing= new_email_form.cleaned_data['is_phishing'],
                                      sender_display_name=new_email_form.cleaned_data['sender_display_name'],
                                      content=handle_uploaded_file(request.FILES['email_file'])
                                      )
            # new_email.save()
            return render(request, 'email_creation.html', {
                'email_creation_form': new_email_form,
                'message': 'success'
            })
        else:
             return render(request, 'email_creation.html', {
                'email_creation_form': PhishingEmailCreationForm(),
                'message': new_email_form.errors
            })
        # return redirect('/')
    else:
        email_creation_form = PhishingEmailCreationForm()
        return render(request, 'email_creation.html', {
            'email_creation_form': email_creation_form
        })


def handle_uploaded_file(f):
    email_content = ''
    for chunk in f.chunks():
        email_content += chunk.decode('utf-8')
    return email_content

