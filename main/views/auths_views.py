# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.contrib.auth import SESSION_KEY, authenticate, login
from django.contrib.auth.models import User
from main.models import UserProfile
from django.contrib import messages

from django.contrib.auth import logout

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.utils.encoding import force_bytes


from django.shortcuts import redirect

def custom_404_view(request, exception):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/dashboard/')
        else:
            return redirect('/')
    else:
        return redirect('/login/')



def login_register_view(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            email = request.POST['email']
            password = request.POST['password']
            users = User.objects.filter(email=email)
            user = None
            for u in users:
                authenticated_user = authenticate(request, username=u.username, password=password)
                if authenticated_user:
                    user = authenticated_user
                    break
            if user:
                login(request, user)
                profile = user.userprofile
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials or user not found')

        elif 'register' in request.POST:
            try:
                email = request.POST['email']
                password = request.POST['password']
                identification_id = request.POST.get('identification_id')
                confirm_password = request.POST['confirm_password']
                if password != confirm_password:
                    messages.error(request, "Las claves no coinciden")
                elif User.objects.filter(email=email).exists():
                    messages.error(request, "Correo ya registrado")


                elif any(
                    profile.id_document == identification_id
                    for profile in UserProfile.objects.all()
                ):
                    messages.error(request, "Cedula o Pasaporte ya registrado")


                else:
                    username = email.split('@')[0]
                    user = User.objects.create_user(username=username, email=email, password=password)
                    UserProfile.objects.create(
                        user=user,
                        first_name=request.POST['first_name'],
                        last_name=request.POST['last_name'],
                        date_of_birth=request.POST['dob'],
                        gender=request.POST['gender'],
                        id_document=request.POST['identification_id'],
                    )
                    messages.success(request, "Creacion Exitosa! Favor Iniciar Sesion.")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")

    return render(request, 'login_register/login_register.html')


def logout_view(request):
    logout(request)  # ends the session
    return redirect('login')  # or wherever you want to send them





def account_recovery(request):
    if request.method == "POST":
        email = request.POST.get('email')
        associated_users = User.objects.filter(email=email)
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Request"
                email_template_name = "user/password-reset-email.txt"
                c = {
                    "email": user.email,
                    'domain': '127.0.0.1:8000',
                    'site_name': 'Reservation App',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                email_content = render_to_string(email_template_name, c)
                send_mail(subject, email_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            messages.success(request, 'Check your email for the password reset link.')
        else:
            messages.error(request, 'No user is associated with this email.')
    return render(request, 'user/account_recovery.html')