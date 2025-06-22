# -*- coding: utf-8 -*-

from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.views.static import serve
from django.conf import settings
from main.views import request_account_deletion
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login/', views.login_register_view, name='login'),


    path('', views.home_view, name='home'),

    # Single URL for requesting reset
    path('password_reset/', views.custom_password_reset_request, name='password_reset'),
        # The link user gets in the email (Django default)
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='main/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='main/password_reset_complete.html'
    ), name='password_reset_complete'),


    path('forgot-password/', views.custom_password_reset_request, name='forgot_password'),
    
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
     

    path('api/search_places/', views.search_places, name='search_places'),


    path('manifest.webmanifest', serve, {'path': 'manifest.webmanifest', 'document_root': settings.STATIC_ROOT[0]}),
    path('service-worker.js', serve, {'path': 'service-worker.js', 'document_root': settings.STATIC_ROOT[0]}),

    path('settings/', views.settings_view, name='settings'),

    path('password_change_form/', auth_views.PasswordChangeView.as_view(template_name='main/password_change_form.html'), name='password_change_form'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='main/password_change_done.html'), name='password_change_done'),
    path('request-deletion/', request_account_deletion, name='request_account_deletion'),
    path('confirm-delete/<uid>/<token>/', views.confirm_account_deletion, name='confirm_account_deletion'),

    path('help/', views.help_view, name='help'),


    path('reserve/<int:place_id>/', views.make_reservation, name='make_reservation'),

    path('reservas/', views.reservations_list, name='reservations_list'),
    path('reservas/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),

]
if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
