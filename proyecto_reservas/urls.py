    # -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from main.views import auths_views  # Ensure this exists and has the view
from django.shortcuts import redirect

# Custom logout view based on staff status
def custom_logout_view(request):
    next_url = '/dashboard/' if request.user.is_staff else '/'
    return auth_views.LogoutView.as_view(next_page=next_url)(request)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('dashboard/', include('proyecto_reservas.admin_urls', namespace='admin_dashboard')),
    path('accounts/logout/', custom_logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
]

# Handle 404 and 500 errors
handler404 = 'main.views.error.custom_404'
handler500 = 'main.views.error.custom_500'