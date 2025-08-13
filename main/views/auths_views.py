# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import SESSION_KEY, authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from main.models import UserProfile

def custom_404_view(request, exception):
    if request.user.is_authenticated:
            return redirect('/')
    else:
        return redirect('/login/')



def login_register_view(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            email = request.POST['email']
            password = request.POST['password']
            print(email, password)
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
                messages.error(request, 'El usuario no existe o la clave esta incorrecta')

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
                    username = email
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

        if not email:
            messages.error(request, 'Por Favor Escribir un correo.')
            return render(request, 'user/account_recovery.html')

        try:
            EmailValidator()(email)
        except ValidationError:
            messages.error(request, 'Formato de correo incorrecto o no permitido.')
            return render(request, 'user/account_recovery.html')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No hay ningun usuario asociado a este correo')
            return render(request, 'user/account_recovery.html')
        except User.MultipleObjectsReturned:
            messages.error(request, 'Multiples Usuarios fueron encontrados con este correo. Favor Contactar Soporte')
            return render(request, 'user/account_recovery.html')

        # Ensure email settings exist AFTER user retrieval
        if not settings.EMAIL_HOST_USER or not settings.DEFAULT_FROM_EMAIL:
            messages.error(request, 'No se pudo mandar un correo de restablecimiento. Contacta con Soporte.')
            return render(request, 'user/account_recovery.html')

        try:
            subject = "Solicitud de cambio de clave"
            email_template_name = "user/password-reset-email.txt"
            context = {
                "email": user.email,
                "domain": "www.tucancha.com.do",
                "site_name": "Reservation App",
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
                "protocol": "https",
            }
            text_content = render_to_string("user/password-reset-email.txt", context)
            html_content = render_to_string("user/password-reset-email.html", context)

            email_msg = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )

            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send()
            messages.success(request,'Si tu correo es valido, recibiras un enlace para restablecer tu clave en breve.')
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            messages.error(request, f'Error al enviar el correo de recuperacion: {str(e)}. Favor Contactar Soporte')
            return render(request, 'user/account_recovery.html')

    return render(request, 'user/account_recovery.html')
