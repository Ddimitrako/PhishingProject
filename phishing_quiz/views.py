from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from phishing_quiz.models import *
from phishing_quiz.forms import *

from django.views.decorators.clickjacking import xframe_options_exempt
import json
from sbam_app.templatetags import custom_tags
from django.shortcuts import redirect
from datetime import datetime
from email_simulation.views import email_preview, handle_uploaded_file
from sbam_app.views import disable_form
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from sbam_app.views import advanced_users_only
from django.utils.translation import gettext_lazy as _


# Create your views here.

@login_required
def phishing_quiz(request, assignment_id):
    if request.user.assignment_set.filter(pk=assignment_id):
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
                new_answer = PhishingEmailAssignmentAnswer.objects.filter(email=true_label, assignment=test_assignment).first()
                print(new_answer)
                new_answer.user_answer=answers[email]['answer']
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
            test_emails = PhishingEmail.objects.filter(is_active=True).filter(phishingemailassignmentanswer__assignment=assignment_id)
            assignment = sbam_models.TestAssignment.objects.get(pk=assignment_id)
            return render(request, 'phishing_quiz.html', {'emails': test_emails,
                                                          'assignment_id': assignment.id,
                                                          'progress_bar': 1 / len(test_emails) * 100})
    else:
        messages.error(request, _('You do not have access to this assignment'))
        return redirect('/')


def phis_email_preview(request):
    return email_preview(request)


@xframe_options_exempt
def email_request(request, email_id):

    email = PhishingEmail.objects.get(id=email_id)
    current_time = datetime.now().strftime("%H:%M")
    current_time = current_time + ' PM' if datetime.now() > datetime.now().replace(hour=12, minute=0) else current_time + ' AM'
    return render(request, 'email_template.html', {'email': email,
                                                   'time': current_time})

@advanced_users_only
def email_creation(request):
    if request.method == 'POST':
        new_email_form = PhishingEmailCreationForm(request.POST, request.FILES)
        print(new_email_form.errors)
        print(new_email_form.is_valid())
        if new_email_form.is_valid():
            msg, content = handle_uploaded_file(request.FILES['email_file'])

            new_email = PhishingEmail(sender_email=new_email_form.cleaned_data['sender_email'],
                                      is_phishing= new_email_form.cleaned_data['is_phishing'],
                                      sender_display_name=new_email_form.cleaned_data['sender_display_name'],
                                      content=content,
                                      title=new_email_form.cleaned_data['email_title'],
                                      )
            new_email.save()
            new_form = PhishingEmailCreationForm(initial={'sender_email': new_email.sender_email,
                                                          'is_phishing': new_email.is_phishing,
                                                          'sender_display_name': new_email.sender_display_name,
                                                          'email_file': request.FILES['email_file']})

            disable_form(new_form)
            return render(request, 'email_creation.html', {
                'mode': 'submitted',
                'email': new_email.id,
                'email_creation_form': new_form,
                'message': 'success'
            })
        else:
             return render(request, 'email_creation.html', {
                'mode': 'error',
                'email_creation_form': PhishingEmailCreationForm(),
                'message': new_email_form.errors
            })
        # return redirect('/')
    else:
        email_creation_form = PhishingEmailCreationForm()
        return render(request, 'email_creation.html', {
            'mode': 'rendered',
            'email_creation_form': email_creation_form
        })




