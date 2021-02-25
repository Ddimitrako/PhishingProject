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
    scheduled_date = datetime.datetime.strptime(start_date+' 10:50:00', '%Y-%m-%d %H:%M:%S')
    email = SimEmail.objects.filter(emailassignment=email_ass.pk).first()
    # print(email.content)
    schedule('django.core.mail.send_mail',
             email.subject,
             '',
             settings.EMAIL_HOST_USER,
             [user.email],
             False,
             None,
             None,
             None,
             link_enriched(email.content, new_assignment.id, email.id),
             schedule_type=Schedule.ONCE,
             next_run=timezone.make_aware(scheduled_date))

    # since the `repeats` defaults to -1
    # this schedule will erase itself after having run


def check_simulation_email(user, email_id):
    email = SimEmail.objects.get(pk=email_id)
    async_task('django.core.mail.send_mail', email.subject,
               '', settings.EMAIL_HOST_USER, [user.email], False, None, None, None, email.content)


def link_enriched(email, ass_id, emali_id):
    return email.replace('https://rb.gy/kmo4ur', 'https://rb.gy/kmo4ur?ass='+str(ass_id)+'&em='+str(emali_id))

# encryption for url /sim_endpoint/

#encryption for online in vm https://rb.gy/kmo4ur

#encryption for localhost https://rb.gy/92erwn