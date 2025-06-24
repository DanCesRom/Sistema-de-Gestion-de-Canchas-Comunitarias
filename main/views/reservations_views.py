from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
import json
from main.models import Place
from main.models import Reservation

import random
import string

import qrcode
from io import BytesIO
import base64


@login_required(login_url='/login/')
def make_reservation(request, place_id):
    place = get_object_or_404(Place, id=place_id)

    # Fecha seleccionada desde el parametro GET o por defecto hoy
    date_str = request.GET.get('date')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.localdate()
    except ValueError:
        date = timezone.localdate()

    today = timezone.localdate()
    error_message = None

    # Evitar reservar en el pasado
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

            # Duracion debe ser positiva
            if start_t >= end_t:
                error_message = "La hora de inicio debe ser antes de la hora de fin."
            
            # Duracion maxima 2 horas (4 bloques de 30min)
            elif (datetime.combine(date, end_t) - datetime.combine(date, start_t)) > timedelta(hours=2):
                error_message = "No puedes reservar mas de 2 horas."

            # Dia de la semana valido
            open_days_list = [d.strip() for d in place.open_days.lower().split(',')]
            weekday = date.strftime('%A').lower()
            if weekday not in open_days_list:
                error_message = f"Este lugar no abre los dias {weekday.capitalize()}."

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
                error_message = "Este horario ya esta reservado."

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
    
    # Generar QR base64 (puedes usar la funcion que ya tienes)
    qr_base64 = generate_qr_base64(reservation.code)

    return render(request, 'reservations/reservation_detail.html', {
        'reservation': reservation,
        'qr_base64': qr_base64,
    })

def generate_unique_code():
    """Genera un codigo unico de 6 caracteres alfanumericos"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Reservation.objects.filter(code=code).exists():
            return code


def generate_qr_base64(data):
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return qr_base64