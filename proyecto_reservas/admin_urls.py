# -*- coding: utf-8 -*-

# proyecto_reservas/admin_urls.py

from django.urls import path
from proyecto_reservas.views import admin_views  # Importar correctamente desde views.admin_views
from django.urls import path, include

app_name = 'admin_dashboard'

urlpatterns = [
    path('', admin_views.admin_dashboard, name='dashboard'),

    #Prueba de Correo Electrónico
    path('settings/test-email/', admin_views.test_email_settings, name='test_email_settings'),

    # Reservations
    path('reservations/', admin_views.reservations_management, name='admin_reservations_management'),
    path('reservations/<int:reservation_id>/', admin_views.reservation_detail, name='admin_reservation_detail'),
    path('reservations/<int:reservation_id>/delete/', admin_views.delete_reservation, name='admin_delete_reservation'),
    path('reservations/<int:reservation_id>/notify/', admin_views.send_reservation_notification, name='send_reservation_notification'),


    # Places
    path('places/', admin_views.places_management, name='admin_places_management'),
    path('places/<int:place_id>/', admin_views.place_detail, name='admin_place_detail'),
    path('places/new/', admin_views.place_detail, name='admin_place_new'),
    path('places/<int:place_id>/delete/', admin_views.admin_place_delete, name='admin_place_delete'),

    # Users
    path('users/', admin_views.users_management, name='admin_users_management'),
    path('users/<int:user_id>/', admin_views.user_detail, name='admin_user_detail'),
    path('users/<int:user_id>/toggle/', admin_views.toggle_user_status, name='admin_toggle_user_status'),

    # Calendar
    path('calendar/', admin_views.calendar_view, name='admin_calendar_view'),

    # Reports
    path('reports/', admin_views.reports_analytics, name='admin_reports_analytics'),
    path('export/', admin_views.export_reservations_csv, name='admin_export_reservations'),

    # Settings
    path('settings/', admin_views.admin_settings, name='admin_settings'),

]


# ...