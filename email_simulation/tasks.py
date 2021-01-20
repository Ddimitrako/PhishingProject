from datetime import timedelta
from django.utils import timezone
from django_q.tasks import async_task, schedule
from django_q.models import Schedule
from django.conf import settings
import datetime
from email_simulation.models import SimEmail
from sbam_app.models import TestAssignment


def simulation_email_schedule(new_assignment, start_date, end_date, email_ass, user):

    msg = 'Welcome to our website scheduled'
    scheduled_date = datetime.datetime.strptime(start_date+' 9:16PM', '%Y-%m-%d %I:%M%p')
    email = SimEmail.objects.filter(emailassignment=email_ass.pk).first()
    # print(email.content)
    schedule('django.core.mail.send_mail',
             'Emails',
             '',
             settings.EMAIL_HOST_USER,
             [user.email],
             False,
             None,
             None,
             None,
             email.content,
             schedule_type=Schedule.ONCE,
             next_run=timezone.make_aware(scheduled_date))

    # since the `repeats` defaults to -1
    # this schedule will erase itself after having run