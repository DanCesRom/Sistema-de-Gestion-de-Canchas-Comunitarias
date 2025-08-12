from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.conf import settings
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode



@login_required(login_url='/login/')
def settings_view(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        # Update name
        profile.first_name = request.POST.get('first_name', profile.first_name)
        profile.last_name = request.POST.get('last_name', profile.last_name)

        # Update email
        request.user.email = request.POST.get('email', request.user.email)

        # Save both
        request.user.save()
        profile.save()
        messages.success(request, "Profile updated.")
        return redirect('settings')

    return render(request, 'settings/settings.html', {
        'user': request.user,
        'profile': profile,
    })



@login_required(login_url='/login/')
def request_account_deletion(request):
    if request.method == "POST":
        email = request.POST.get('email')
        associated_users = User.objects.filter(email=email)
        if associated_users.exists():
            for user in associated_users:
                subject = "Confirm Account Deletion"
                email_template_name = "settings/account_deletion_email.txt"
                c = {
                    "email": user.email,
                    'domain': '127.0.0.1:8000',
                    'site_name': 'Reservation App',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                    'protocol': 'https',
                }
                email_content = render_to_string(email_template_name, c)
                send_mail(subject, email_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            messages.success(request, 'Check your email to confirm account deletion.')
        else:
            messages.error(request, 'No user is associated with this email.')
    return redirect('settings')  # Replace with your actual settings page name


def confirm_account_deletion(request, uid, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)

        # Aqui hara validacion de token

        user.delete()
        messages.success(request, "Tu cuenta ha sido eliminada exitosamente.")
        return redirect('login')

    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, "El enlace de eliminacion no es valido o ha expirado.")
        return redirect('login')