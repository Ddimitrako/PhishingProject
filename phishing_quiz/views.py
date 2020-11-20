from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from phishing_quiz.models import *
from phishing_quiz.forms import *
from django.views.decorators.clickjacking import xframe_options_exempt




# Create your views here.
def phishing_quiz(request):
    if request.method == 'POST':
        print(request.POST['data'])


        # FOR DEMO PURPOSES ONLY
        answers = {
            'email_1': 'true',
            'email_2': 'false',
            'email_3': 'true',
            'email_4': 'false'
        }

        return JsonResponse({'mpompa':1})

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

@xframe_options_exempt
def email_request(request, email_id):
    print(email_id)
    email = PhishingEmail.objects.get(id=email_id)
    print(email.content)
    return HttpResponse(email.content)