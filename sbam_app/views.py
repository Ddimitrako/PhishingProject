from django.shortcuts import render
from django.views.generic import *

from sbam_app.models import *


def DashboardView(request):
    return render(request, 'dashboard.html')


class PersonsView(ListView):
    queryset = Person.objects.filter(user__is_active=True)
    template_name = 'users.html'
