from datetime import timedelta
from django.utils import timezone
from django_q.tasks import async_task, schedule
from django_q.models import Schedule
from django.conf import settings
import datetime
from email_simulation.models import SimEmail, EmailAssignment
import sbam_app.models as sbam_models


def simulation_email_schedule(new_assignment, start_date, end_date, email_ass, user):

    msg = 'Welcome to our website scheduled'
    scheduled_date = datetime.datetime.strptime(start_date+' 9:55pM', '%Y-%m-%d %I:%M%p')
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
             link_enriched(email.content, email.id, new_assignment.id),
             schedule_type=Schedule.ONCE,
             next_run=timezone.make_aware(scheduled_date))

    # schedule to create the AssignmentResult object when the campaign ends - User passed the test
    scheduled_date = datetime.datetime.strptime(end_date+' 9:56pM', '%Y-%m-%d %I:%M%p')

    schedule('email_simulation.tasks.simulation_test_pass',
             # args=str(new_assignment.id) + ', ' + str(email.id),
             new_assignment.id,
             email.id,
             schedule_type=Schedule.ONCE,
             next_run=timezone.make_aware(scheduled_date))

    # since the `repeats` defaults to -1
    # this schedule will erase itself after having run


def check_simulation_email(user, email_id):
    email = SimEmail.objects.get(pk=email_id)
    async_task('django.core.mail.send_mail', email.subject,
               '', settings.EMAIL_HOST_USER, [user.email], False, None, None, None, link_enriched(email.content, email.id))


def link_enriched(email, email_id, ass_id=-1):
    if ass_id == -1:
        return email.replace(settings.ENCRYPTED_ENDPOINT, settings.ENCRYPTED_ENDPOINT+'?em=' + str(email_id))
    else:
        return email.replace(settings.ENCRYPTED_ENDPOINT, settings.ENCRYPTED_ENDPOINT+'?ass='+str(ass_id)+'&em='+str(email_id))


def simulation_test_pass(assignment, email):
    sim_assignment = EmailAssignment.objects.filter(assignment_id=assignment, email_id=email).first()
    assignment_result = sbam_models.AssignmentResult(assignment_id=sim_assignment.assignment.id, score=1.0, answer_time=datetime.datetime.now())
    assignment_result.save()
    return True
