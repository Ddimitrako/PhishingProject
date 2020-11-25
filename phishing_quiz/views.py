from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from phishing_quiz.models import *
from phishing_quiz.forms import *
from django.views.decorators.clickjacking import xframe_options_exempt
import json
from sbam_app.templatetags import custom_tags


# Create your views here.
def phishing_quiz(request):
    if request.method == 'POST':
        # print(request.POST['data'])

        answers = json.loads(request.POST['data'])
        emails_ids = []
        print(answers)
        for email in answers:
            emails_ids.append(int(answers[email]['id']))

        labels = PhishingEmail.objects.filter(pk__in=emails_ids)
        print(labels)
        # campaign = sbam_models.Campaign(pk=13)

        # na fernw to swsto assignment
        test_assignment = sbam_models.TestAssignment.objects.get(pk=52)
        correct_answers = 0
        for true_label, email in zip(labels, answers):
            print(true_label.is_phishing, answers[email]['answer'])
            new_answer = PhishingEmailAssignmentAnswer(email=true_label, user_answer=answers[email]['answer'], assignment=test_assignment)
            new_answer.save()
            if true_label.is_phishing == answers[email]['answer']:
                correct_answers += 1

        quiz_score = PhishingEmailQuizScore(assignment=test_assignment, score=correct_answers / len(labels) * 100)
        quiz_score.save()
        return JsonResponse({
                             'score': correct_answers / len(labels) * 100,
                             'score_badge': custom_tags.get_badge(str(correct_answers / len(labels) * 100)),
                         })

    else:

        # na dialegeis 10 random emails otan ftiaxtei
        # Na koitaei ti exei apanthsei kai se poia exei kanei lathos etsi wste na dinetai proteraiothta se auta
        test_emails = PhishingEmail.objects.all()
        return render(request, 'phishing_quiz.html', {'emails': test_emails,
                                                      'progress_bar': 1 / len(test_emails) * 100})

@xframe_options_exempt
def email_request(request, email_id):
    print(email_id)
    email = PhishingEmail.objects.get(id=email_id)
    print(email.content)
    return HttpResponse(email.content)
