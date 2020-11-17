from django.shortcuts import render
from django.http import HttpResponse
from phishing_quiz.forms import *

# Create your views here.
def phishing_quiz(request):
    if request.method == 'POST':
        print(request.POST['email_1'])
        print(request.POST['email_2'])
        print(request.POST['email_3'])


        # FOR DEMO PURPOSES ONLY
        answers = {
            'email_1': 'true',
            'email_2': 'false',
            'email_3': 'true'
        }

        return HttpResponse(request, 'phishing_quiz.html', {
            'mode': 'results',
            'email_1_answer': request.POST['email_1'],
            'email_2_answer': request.POST['email_2'],
            'email_3_answer': request.POST['email_3'],
            'email_1': 'true' if answers['email_1'] == request.POST['email_1'] else 'false',
            'email_2': 'true' if answers['email_2'] == request.POST['email_2'] else 'false',
            'email_3': 'true' if answers['email_3'] == request.POST['email_3'] else 'false',
        })
    else:
        form1 = Phishing_Quiz()
        form2 = Phishing_Quiz()
        form3 = Phishing_Quiz()
        return render(request, 'phishing_quiz.html', {
            'mode': 'quiz',
            'email_1': form1,
            'email_2': form2,
            'email_3': form3,
        })
