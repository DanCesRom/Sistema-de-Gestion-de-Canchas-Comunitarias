# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import SESSION_KEY, authenticate, login
from django.contrib.auth.models import User
from main.models import UserProfile
from datetime import datetime
from .models import Reservation
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.conf import settings


from django.contrib import messages
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode


def login_register_view(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            email = request.POST['email']
            password = request.POST['password']
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user:
                    login(request, user)

                    # Get profile and check biometric
                    profile = user.userprofile
                    #if not profile.biometric_enabled:
                        #return redirect('biometric_consent')
                    #else:
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid credentials')
            except User.DoesNotExist:
                messages.error(request, 'User not found')

        elif 'register' in request.POST:
            try:
                email = request.POST['email']
                password = request.POST['password']
                confirm_password = request.POST['confirm_password']
                if password != confirm_password:
                    messages.error(request, "Passwords do not match")
                elif User.objects.filter(email=email).exists():
                    messages.error(request, "Email already registered")
                else:
                    username = email.split('@')[0]
                    user = User.objects.create_user(username=username, email=email, password=password)
                    UserProfile.objects.create(
                        user=user,
                        first_name=request.POST['first_name'],
                        last_name=request.POST['last_name'],
                        date_of_birth=request.POST['dob'],
                        gender=request.POST['gender']
                    )
                    messages.success(request, "Registered successfully! Please log in.")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")

    return render(request, 'main/login_register.html')


def custom_password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        associated_users = User.objects.filter(email=email)
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Request"
                email_template_name = "main/password_reset_email.txt"
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
    return render(request, 'main/password_reset.html')





from .models import Place
import json






@login_required(login_url='/login/')
def home_view(request):
    places = Place.objects.all()
    places_json = [
        {
            'id': p.id,
            'name': p.name,
            'latitude': p.latitude,
            'longitude': p.longitude,
            'description': p.description,
            'sport_type': p.sport_type,
            'image_url': p.image_url,
            'open_time': p.open_time.strftime('%H:%M') if p.open_time else '',
            'close_time': p.close_time.strftime('%H:%M') if p.close_time else '',
            'open_days': p.open_days,
        } for p in places
    ]
    return render(request, 'main/home.html', {'places': json.dumps(places_json)})


from django.http import JsonResponse
from main.models import Place





@login_required(login_url='/login/')
def search_places(request):
    q = request.GET.get('q', '')
    results = []
    if q:
        places = Place.objects.filter(name__icontains=q)[:10]  # limit to 10 results
        for place in places:
            results.append({
                'id': place.id,
                'name': place.name,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'sport_type': place.sport_type,
                'image_url': place.image_url,
                'open_time': place.open_time.strftime('%H:%M') if place.open_time else '',
                'close_time': place.close_time.strftime('%H:%M') if place.close_time else '',
                'open_days': place.open_days,
                'description': place.description,
            })
    return JsonResponse(results, safe=False)



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

    return render(request, 'main/settings.html', {
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
                email_template_name = "main/account_deletion_email.txt"
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
            messages.success(request, 'Check your email to confirm account deletion.')
        else:
            messages.error(request, 'No user is associated with this email.')
    return redirect('settings')  # Replace with your actual settings page name



def confirm_account_deletion(request, uid, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)

        # Aquí deberías validar el token (esto depende de cómo lo generas)
        # Por ahora suponemos que es válido

        user.delete()
        messages.success(request, "Tu cuenta ha sido eliminada exitosamente.")
        return redirect('login')

    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, "El enlace de eliminacion no es valido o ha expirado.")
        return redirect('login')



@login_required(login_url='/login/')
def help_view(request):
    return render(request, 'main/help.html')





from django.shortcuts import render, redirect, get_object_or_404
from .models import Place, Reservation
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
import json
import random
import string

def generate_unique_code():
    """Genera un código único de 6 caracteres alfanuméricos"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Reservation.objects.filter(code=code).exists():
            return code

@login_required(login_url='/login/')
def make_reservation(request, place_id):
    place = get_object_or_404(Place, id=place_id)

    # Fecha seleccionada desde el parámetro GET o por defecto hoy
    date_str = request.GET.get('date')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.localdate()
    except ValueError:
        date = timezone.localdate()

    today = timezone.localdate()
    error_message = None

    # ⚠️ Evitar reservar en el pasado
    if date < today:
        error_message = "No se pueden hacer reservas en fechas pasadas."
        context = {
            'place': place,
            'date': date,
            'reserved_blocks_json': json.dumps([]),
            'open_time': place.open_time.strftime('%H:%M'),
            'close_time': place.close_time.strftime('%H:%M'),
            'error_message': error_message,
        }
        return render(request, 'reservations/make_reservation.html', context)

    # Buscar reservas existentes para ese lugar y día
    reservations = Reservation.objects.filter(place=place, date=date)
    reserved_blocks = []

    for r in reservations:
        if not r.start_time or not r.end_time:
            continue
        current = datetime.combine(date, r.start_time)
        end_dt = datetime.combine(date, r.end_time)

        while current < end_dt:
            reserved_blocks.append(current.strftime('%H:%M'))
            current += timedelta(minutes=30)

    # Procesar POST (nueva reserva)
    if request.method == 'POST':
        try:
            start_t = datetime.strptime(request.POST['start_time'], '%H:%M').time()
            end_t = datetime.strptime(request.POST['end_time'], '%H:%M').time()

            # Duración debe ser positiva
            if start_t >= end_t:
                error_message = "La hora de inicio debe ser antes de la hora de fin."
            
            # Duración máxima 2 horas (4 bloques de 30min)
            elif (datetime.combine(date, end_t) - datetime.combine(date, start_t)) > timedelta(hours=2):
                error_message = "No puedes reservar más de 2 horas."

            # Día de la semana válido
            open_days_list = [d.strip() for d in place.open_days.lower().split(',')]
            weekday = date.strftime('%A').lower()
            if weekday not in open_days_list:
                error_message = f"Este lugar no abre los días {weekday.capitalize()}."

            # Hora dentro del horario de apertura
            elif start_t < place.open_time or end_t > place.close_time:
                error_message = "Horario fuera del rango de apertura."

            # Solapamiento con otras reservas
            elif Reservation.objects.filter(
                place=place,
                date=date,
                start_time__lt=end_t,
                end_time__gt=start_t
            ).exists():
                error_message = "Este horario ya está reservado."

            # Si todo está bien, crear reserva
            else:
                reservation=Reservation.objects.create(
                    user=request.user,
                    place=place,
                    date=date,
                    start_time=start_t,
                    end_time=end_t,
                    confirmed=True,
                    code=generate_unique_code()
                )
                qr_base64 = generate_qr_base64(reservation.code)
                return render(request, 'reservations/reservation_success.html', {
                    'reservation': reservation,
                    'qr_base64': qr_base64,
                })

        except Exception as e:
            print("Error en el formulario de reserva:", e)
            error_message = "Hubo un error al procesar la reserva."

    context = {
        'place': place,
        'date': date,
        'reserved_blocks_json': json.dumps(reserved_blocks),
        'open_time': place.open_time.strftime('%H:%M'),
        'close_time': place.close_time.strftime('%H:%M'),
        'error_message': error_message,
    }
    return render(request, 'reservations/make_reservation.html', context)


import qrcode
from io import BytesIO
import base64



def generate_qr_base64(data):
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return qr_base64




@login_required(login_url='/login/')
def reservations_list(request):
    user = request.user
    today = timezone.localdate()
    one_month_ago = today - timedelta(days=30)

    # Reservas activas: fecha desde hoy en adelante
    active_reservations = Reservation.objects.filter(
        user=user,
        date__gte=today
    ).order_by('date', 'start_time')

    # Reservas expiradas recientes: fecha menor a hoy pero no más viejas que un mes
    expired_reservations = Reservation.objects.filter(
        user=user,
        date__lt=today,
        date__gte=one_month_ago
    ).order_by('-date', '-start_time')

    context = {
        'active_reservations': active_reservations,
        'expired_reservations': expired_reservations,
    }
    return render(request, 'reservations/reservations.html', context)




@login_required(login_url='/login/')
def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    # Generar QR base64 (puedes usar la función que ya tienes)
    qr_base64 = generate_qr_base64(reservation.code)

    return render(request, 'reservations/reservation_detail.html', {
        'reservation': reservation,
        'qr_base64': qr_base64,
    })


