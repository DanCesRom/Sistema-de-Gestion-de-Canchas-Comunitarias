from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from main.models import Place, Reservation, UserProfile, FAQ, SupportContact
from proyecto_reservas.forms import PlaceForm, ReservationForm, UserProfileForm, AdminSettingsForm
import csv
import json
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

from django.db.models.functions import ExtractWeekDay

def is_admin(user):
    return user.is_staff or user.is_superuser

@csrf_exempt
def test_email_settings(request):
    if request.method == 'POST':
        try:
            send_mail(
                subject='Correo de prueba desde el sistema',
                message='Este es un correo de prueba para verificar la configuracion del sistema.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['toolsdancesrom@hotmail.com'],
                fail_silently=False,
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Metodo no permitido'})




@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard with overview statistics"""
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Statistics
    total_users = User.objects.count()
    total_places = Place.objects.count()
    reservations_this_week = Reservation.objects.filter(
        created_at__date__gte=week_start
    ).count()
    
    # Today's reservations
    today_reservations = Reservation.objects.filter(date=today).select_related('place', 'user')
    
    # Upcoming reservations (next 7 days)
    upcoming_reservations = Reservation.objects.filter(
        date__gte=today,
        date__lte=today + timedelta(days=7)
    ).select_related('place', 'user').order_by('date', 'start_time')[:10]
    
    # Field availability today
    places_availability = []
    for place in Place.objects.all():
        reservations_count = Reservation.objects.filter(
            place=place,
            date=today
        ).count()
        places_availability.append({
            'place': place,
            'reservations_today': reservations_count,
            'is_available': reservations_count < 10  # Assuming max 10 slots per day
        })
    
    context = {
        'total_users': total_users,
        'total_places': total_places,
        'reservations_this_week': reservations_this_week,
        'today_reservations': today_reservations,
        'upcoming_reservations': upcoming_reservations,
        'places_availability': places_availability,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)

@user_passes_test(is_admin)
def reservations_management(request):
    """Manage all reservations with filtering"""
    reservations = Reservation.objects.select_related('user', 'place').order_by('-created_at')
    
    # Filtering
    place_filter = request.GET.get('place')
    try:
        place_filter_int = int(place_filter) if place_filter else None
    except ValueError:
        place_filter_int = None

    if place_filter_int:
        reservations = reservations.filter(place_id=place_filter_int)

    date_filter = request.GET.get('date')
    user_filter = request.GET.get('user')
    if user_filter and user_filter.lower() != 'none':
        reservations = reservations.filter(user__username__icontains=user_filter)
    status_filter = request.GET.get('status')

    print("Filters:", place_filter, date_filter, user_filter, status_filter)  # <-- Agrega esto
    
    if place_filter:
        reservations = reservations.filter(place_id=place_filter)
    if date_filter:
        reservations = reservations.filter(date=date_filter)
    if user_filter:
        reservations = reservations.filter(user__username__icontains=user_filter)
    if status_filter == 'confirmed':
        reservations = reservations.filter(confirmed=True)
    elif status_filter == 'pending':
        reservations = reservations.filter(confirmed=False)
    
    # Pagination
    paginator = Paginator(reservations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    places = Place.objects.all()
    
    context = {
        'page_obj': page_obj,
        'places': places,
        'current_filters': {
            'place': place_filter_int,  # use the int value
            'date': date_filter,
            'user': user_filter,
            'status': status_filter,
        }
    }
    
    return render(request, 'admin_dashboard/reservations_management.html', context)

from datetime import datetime, timedelta

@user_passes_test(is_admin)
def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reservation updated successfully!')
            return redirect('admin_dashboard:admin_reservations_management')
    else:
        form = ReservationForm(instance=reservation)

    # Compute confirmed count
    user_reservations = reservation.user.reservation_set.all()
    confirmed_count = user_reservations.filter(confirmed=True).count()

    # Calculate duration between start_time and end_time
    start = datetime.combine(datetime.today(), reservation.start_time)
    end = datetime.combine(datetime.today(), reservation.end_time)
    duration = end - start  # returns timedelta

    context = {
        'reservation': reservation,
        'form': form,
        'confirmed_count': confirmed_count,
        'duration': duration,  # send to template
    }

    return render(request, 'admin_dashboard/reservation_detail.html', context)

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

@require_POST
def send_reservation_notification(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    # Your logic to send email here
    return JsonResponse({'message': 'Notification sent'})


@user_passes_test(is_admin)
def admin_place_delete(request, place_id):
    place = get_object_or_404(Place, id=place_id)

    if request.method == "POST":
        place.delete()
        messages.success(request, f'Place "{place.name}" eliminado correctamente.')
        return redirect('admin_dashboard:admin_places_management')  # Ajusta esta ruta al listado

    # Si quieres mostrar un template de confirmacion:
    return render(request, 'admin_dashboard/place_confirm_delete.html', {'place': place})


@user_passes_test(is_admin)
def places_management(request):
    """Manage all places/fields"""
    places = Place.objects.all().order_by('name')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        places = places.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(sport_type__icontains=search)
        )
    else:
        search = ''
    
    context = {
        'places': places,
        'search': search,
    }
    
    return render(request, 'admin_dashboard/places_management.html', context)

@user_passes_test(is_admin)
def place_detail(request, place_id=None):
    """Add or edit a place"""
    place = get_object_or_404(Place, id=place_id) if place_id else None
    
    if request.method == 'POST':
        form = PlaceForm(request.POST, instance=place)
        if form.is_valid():
            place = form.save()
            messages.success(request, f'Place "{place.name}" saved successfully!')
            return redirect('admin_dashboard:admin_places_management')
    else:
        form = PlaceForm(instance=place)
    
    context = {
        'form': form,
        'place': place,
        'is_edit': place is not None,
    }
    
    return render(request, 'admin_dashboard/place_detail.html', context)

@user_passes_test(is_admin)
def users_management(request):
    """Manage all users"""
    users = User.objects.select_related('userprofile').order_by('-date_joined')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    else:
        search = ''

    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'admin_dashboard/users_management.html', context)

@user_passes_test(is_admin)
def user_detail(request, user_id):
    """View user details and booking history"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user's reservations
    reservations = Reservation.objects.filter(user=user).select_related('place').order_by('-created_at')
    
    # User statistics
    total_reservations = reservations.count()
    confirmed_reservations = reservations.filter(confirmed=True).count()
    upcoming_reservations = reservations.filter(date__gte=timezone.now().date()).count()
    
    context = {
        'user': user,
        'reservations': reservations[:10],  # Show last 10
        'total_reservations': total_reservations,
        'confirmed_reservations': confirmed_reservations,
        'upcoming_reservations': upcoming_reservations,
    }
    
    return render(request, 'admin_dashboard/user_detail.html', context)

@user_passes_test(is_admin)
def calendar_view(request):
    """Calendar view of all reservations"""
    # Get current month or requested month
    year = int(request.GET.get('year', timezone.now().year))
    month_str = request.GET.get('month')
    if month_str and month_str.isdigit():
        month = int(month_str)
    else:
        month = timezone.now().month
    
    # Get reservations for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    reservations = Reservation.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).select_related('place', 'user')
    
    # Group reservations by date
    reservations_by_date = {}
    for reservation in reservations:
        date_key = reservation.date.strftime('%Y-%m-%d')
        if date_key not in reservations_by_date:
            reservations_by_date[date_key] = []
        reservations_by_date[date_key].append(reservation)
    
    context = {
        'year': year,
        'month': month,
        'reservations_by_date': json.dumps(reservations_by_date, default=str),
        'places': Place.objects.all(),
    }
    
    return render(request, 'admin_dashboard/calendar_view.html', context)

@user_passes_test(is_admin)
def reports_analytics(request):
    """Reports and analytics dashboard"""
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Most used places
    most_used_places = Place.objects.annotate(
        reservation_count=Count('reservation')
    ).order_by('-reservation_count')[:5]
    
    # Reservations by day of week
    reservations_by_weekday = Reservation.objects.filter(
        date__gte=month_start
    ).annotate(
        weekday=ExtractWeekDay('date')
    ).values('weekday').annotate(
        count=Count('id')
    ).order_by('weekday')
    
    # Monthly reservations trend
    monthly_reservations = Reservation.objects.filter(
        date__gte=today - timedelta(days=365)
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    context = {
        'most_used_places': most_used_places,
        'reservations_by_weekday': list(reservations_by_weekday),
        'monthly_reservations': list(monthly_reservations),
    }
    
    return render(request, 'admin_dashboard/reports_analytics.html', context)

@user_passes_test(is_admin)
def export_reservations_csv(request):
    """Export reservations to CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reservations.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'User', 'Place', 'Date',
        'Start Time', 'End Time', 'Confirmed', 'Created At'
    ])
    
    reservations = Reservation.objects.select_related('user', 'place').all()
    
    for reservation in reservations:
        writer.writerow([
            reservation.id,
            reservation.user.username if reservation.user else '---',
            reservation.place.name if reservation.place else '---',
            reservation.date.strftime('%Y-%m-%d') if reservation.date else '---',
            reservation.start_time.strftime('%H:%M') if reservation.start_time else '---',
            reservation.end_time.strftime('%H:%M') if reservation.end_time else '---',
            'Yes' if reservation.confirmed else 'No',
            reservation.created_at.strftime('%Y-%m-%d %H:%M:%S') if reservation.created_at else '---',
        ])
    
    return response

@user_passes_test(is_admin)
def admin_settings(request):
    """Admin settings and configurations"""
    if request.method == 'POST':
        # Handle settings update
        messages.success(request, 'Settings updated successfully!')
        return redirect('admin_settings')
    
    # Get current settings (you might want to create a Settings model)
    context = {
        'settings': {
            'max_bookings_per_week': 5,
            'time_slot_duration': 60,
            'notifications_enabled': True,
        }
    }
    
    return render(request, 'admin_dashboard/settings.html', context)

@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    """Toggle user active status (ban/unban)"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f'User {user.username} has been {status}.')
    
    return redirect('/dashboard/users/')

@user_passes_test(is_admin)
def delete_reservation(request, reservation_id):
    """Delete a reservation"""
    if request.method == 'POST':
        reservation = get_object_or_404(Reservation, id=reservation_id)
        reservation.delete()
        messages.success(request, 'Reservation deleted successfully!')
    
    return redirect('admin_dashboard:admin_reservations_management')