# -*- coding: utf-8 -*-

from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import auths_views, reservations_views, settings_views, help_views, home_views


urlpatterns = [

    #login and registration views
    path('login/', views.auths_views.login_register_view, name='login'),

    #Password reset user views
    path('user/account-recovery/', views.auths_views.account_recovery, name='account-recovery'),

    # Form para ingresar nueva clave
    path('user/password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
            template_name='user/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete')  # <-- aquí redirige a tu template custom
        ),
        name='password_reset_confirm'
    ),

    # Pagina de confirmacion de exito
    path(
        'user/password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='user/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),



     #Main app map and menu views 
    path('', views.home_views.home_view, name='home'),
    path('api/search_places/', views.home_views.search_places, name='search_places'),



    #Reservation Views
    path('reserve/<int:place_id>/', views.reservations_views.make_reservation, name='make_reservation'),
    path('reservas/', views.reservations_views.reservations_list, name='reservations_list'),
    path('reservas/<int:reservation_id>/', views.reservations_views.reservation_detail, name='reservation_detail'),


    #Help Views
    path('help/', views.help_views.help_view, name='help'),


    #Settings Views
    path('settings/', views.settings_views.settings_view, name='settings'),
    path('password-change/form/', auth_views.PasswordChangeView.as_view(template_name='settings/password_change_form.html'), name='password_change_form'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='settings/password_change_done.html'), name='password_change_done'),

    path('request-deletion/', views.settings_views.request_account_deletion, name='request_account_deletion'),
    path('confirm-delete/<uid>/<token>/', views.settings_views.confirm_account_deletion, name='confirm_account_deletion'),


    

    path('manifest.webmanifest', serve, {'path': 'manifest.webmanifest', 'document_root': settings.STATIC_ROOT}),
    path('service-worker.js', serve, {'path': 'service-worker.js', 'document_root': settings.STATIC_ROOT})
 
]


if settings.DEBUG == False:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)