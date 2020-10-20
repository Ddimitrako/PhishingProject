from django.shortcuts import render
from password_strength.forms import *
from zxcvbn_password import zxcvbn
from django.http import JsonResponse

# Create your views here.


def password_strength(request):
    if request.method == 'POST':
        # print(request.POST)
        pass_1 = request.POST['pass_1']
        pass_2 = request.POST['pass_2']
        pass_3 = request.POST['pass_3']
        result_dict = {
            'pass_1': {
                'pass': zxcvbn(pass_1)['password'],
                'score': zxcvbn(pass_1)['score'],
                'crack_display': zxcvbn(pass_1)['crack_times_display']['offline_fast_hashing_1e10_per_second'],
                'suggestions': zxcvbn(pass_1)['feedback']['suggestions']
            },
            'pass_2': {
                'pass': zxcvbn(pass_2)['password'],
                'score': zxcvbn(pass_2)['score'],
                'crack_display': zxcvbn(pass_2)['crack_times_display']['offline_fast_hashing_1e10_per_second'],
                'suggestions': zxcvbn(pass_2)['feedback']['suggestions']
            },
            'pass_3': {
                'pass': zxcvbn(pass_3)['password'],
                'score': zxcvbn(pass_3)['score'],
                'crack_display': zxcvbn(pass_3)['crack_times_display']['offline_fast_hashing_1e10_per_second'],
                'suggestions': zxcvbn(pass_3)['feedback']['suggestions']
            }
        }

        for key in zxcvbn(pass_1):
            print(key, zxcvbn(pass_1)[key])

        return JsonResponse({'data': result_dict})
    else:
        return render(request, 'password_strength.html', {
            'pass_check_form': PasswordStrengthForm()
        })
