from django.shortcuts import render
from django.views.generic import *

from sbam_app.models import *


def DashboardView(request):
    return render(request, 'dashboard.html')


class PersonsView(ListView):
    model = Person
    template_name = 'users.html'
    context_object_name = 'users_list'
