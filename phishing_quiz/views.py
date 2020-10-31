from django.shortcuts import render


# Create your views here.
def phishing_quiz(request):
    return render(request, 'phishing_quiz.html')
