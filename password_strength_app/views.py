from django.shortcuts import render
from password_strength_app.forms import *
from zxcvbn_password import zxcvbn
from django.http import JsonResponse
from password_strength import PasswordPolicy
from sbam_app.models import *
from sbam_app.templatetags import custom_tags
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from sbam_app.views import threats_calculation
# Create your views here.

@login_required
def password_strength(request, assignment_id):
    if request.user.assignment_set.filter(pk=assignment_id):
        if request.method == 'POST':

            policy = PasswordPolicy()
            pass_1 = request.POST['pass_1']
            pass_2 = request.POST['pass_2']
            pass_3 = request.POST['pass_3']
            result_dict = {
                'pass_1': {
                    'score': policy.password(pass_1).strength() * 100,
                    'badge': custom_tags.get_badge(str(policy.password(pass_1).strength() * 100)),
                    'crack_display': zxcvbn(pass_1)['crack_times_display']['offline_fast_hashing_1e10_per_second'],
                    'weakness_factor': policy.password(pass_1).weakness_factor,
                    'suggestions': zxcvbn(pass_1)['feedback']['suggestions']
                },
                'pass_2': {
                    'score': policy.password(pass_2).strength() * 100,
                    'badge': custom_tags.get_badge(str(policy.password(pass_2).strength() * 100)),
                    'crack_display': zxcvbn(pass_2)['crack_times_display']['offline_fast_hashing_1e10_per_second'],
                    'weakness_factor': policy.password(pass_2).weakness_factor,
                    'suggestions': zxcvbn(pass_2)['feedback']['suggestions']
                },
                'pass_3': {
                    'score': policy.password(pass_3).strength() * 100,
                    'badge': custom_tags.get_badge(str(policy.password(pass_3).strength() * 100)),
                    'crack_display': zxcvbn(pass_3)['crack_times_display']['offline_fast_hashing_1e10_per_second'],
                    'weakness_factor': policy.password(pass_3).weakness_factor,
                    'suggestions': zxcvbn(pass_3)['feedback']['suggestions']
                },
            }

            if policy.password(pass_1).letters_lowercase == 0 or policy.password(pass_1).letters_uppercase == 0:
                result_dict['pass_1']['suggestions'].append('You should provide both lowercase-uppercase letters')

            if policy.password(pass_2).letters_lowercase == 0 or policy.password(pass_2).letters_uppercase == 0:
                result_dict['pass_2']['suggestions'].append('You should provide both lowercase-uppercase letters')

            if policy.password(pass_3).letters_lowercase == 0 or policy.password(pass_3).letters_uppercase == 0:
                result_dict['pass_3']['suggestions'].append('You should provide both lowercase-uppercase letters')

            if policy.password(pass_1).numbers == 0:
                result_dict['pass_1']['suggestions'].append('You should use one or more digital digits')

            if policy.password(pass_2).numbers == 0:
                result_dict['pass_2']['suggestions'].append('You should use one or more digital digits')

            if policy.password(pass_3).numbers == 0:
                result_dict['pass_3']['suggestions'].append('You should use one or more digital digits')

            if policy.password(pass_1).special_characters == 0:
                result_dict['pass_1']['suggestions'].append('You should include special characters, such as @#!$')

            if policy.password(pass_2).special_characters == 0:
                result_dict['pass_2']['suggestions'].append('You should include special characters, such as @#!$')

            if policy.password(pass_3).special_characters == 0:
                result_dict['pass_3']['suggestions'].append('You should include special characters, such as @#!$')

            current_user = User.objects.get(pk=request.user.id)

            pass1_has_pers_info = False
            if current_user.username.lower() in pass_1.lower() or current_user.password.lower() in pass_1.lower() or current_user.first_name.lower() in pass_1.lower()\
                    or current_user.last_name.lower() in pass_1.lower()  in pass_1:
                result_dict['pass_1']['suggestions'].append('You should avoid using words found in your personal information')
                pass1_has_pers_info = True

            pass2_has_pers_info = False
            if current_user.username.lower() in pass_2.lower() or current_user.password.lower() in pass_2.lower() or current_user.first_name.lower() in pass_2.lower() \
                    or current_user.last_name.lower() in pass_2.lower():
                result_dict['pass_2']['suggestions'].append('You should avoid using words found in your personal information')
                pass2_has_pers_info = True

            pass3_has_pers_info = False
            if current_user.username.lower() in pass_3.lower() or current_user.password.lower() in pass_3.lower() or current_user.first_name.lower() in pass_3.lower() \
                    or current_user.last_name.lower() in pass_3.lower():
                result_dict['pass_3']['suggestions'].append('You should avoid using words found in your personal information')
                pass2_has_pers_info = False

            if not pass1_has_pers_info:
                if current_user.userprofile.birth_date:
                    if current_user.userprofile.birth_date.strftime('%Y') in pass_1\
                        or current_user.userprofile.birth_date.strftime('%m') in pass_1 or current_user.userprofile.birth_date.strftime('%d') in pass_1:
                        result_dict['pass_1']['suggestions'].append(
                            'You should avoid using words found in your personal information')

            if not pass2_has_pers_info:
                if current_user.userprofile.birth_date:
                    if current_user.userprofile.birth_date.strftime('%Y') in pass_2\
                        or current_user.userprofile.birth_date.strftime('%m') in pass_2 or current_user.userprofile.birth_date.strftime('%d') in pass_2:
                        result_dict['pass_2']['suggestions'].append(
                            'You should avoid using words found in your personal information')

            if not pass3_has_pers_info:
                if current_user.userprofile.birth_date:
                    if current_user.userprofile.birth_date.strftime('%Y') in pass_3\
                        or current_user.userprofile.birth_date.strftime('%m') in pass_3 or current_user.userprofile.birth_date.strftime('%d') in pass_3:
                        result_dict['pass_3']['suggestions'].append(
                            'You should avoid using words found in your personal information')

            mean_score = ((policy.password(pass_1).strength() +
                                                 policy.password(pass_2).strength() +
                                                 policy.password(pass_3).strength()) / 3)

            test_assignment = TestAssignment.objects.get(pk=request.POST['ass_id'])
            assignment_result = AssignmentResult(assignment=test_assignment,
                                                 score=mean_score,
                                                 answer_time=datetime.now())

            assignment_result.save()

            threats_calculation()

            return JsonResponse({'data': result_dict,
                                 'total_score': mean_score * 100,
                                 'total_score_badge': custom_tags.get_badge(str(mean_score)),
                                 })
        else:
            assignment = TestAssignment.objects.get(pk=assignment_id)
            if assignment.status == 'OPEN':
                return render(request, 'password_strength.html', {
                    'pass_check_form': MyPasswordStrengthForm(),
                    'ass_id': assignment.id
                })
            else:
                messages.error(request, _('Assignment \"%(title)s\" is not active for completion! '
                                          'Please select an active assignment from the ones presented in your dashboard...'
                                          % {'title': assignment.test}))
                return redirect('sbam:dashboard')

    else:
        messages.error(request, _('You do not have access to this assignment'))
        return redirect('/')

#