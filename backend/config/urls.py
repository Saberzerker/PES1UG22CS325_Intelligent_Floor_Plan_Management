# """
# Main URL Configuration
# """

# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static

# urlpatterns = [
#     path('admin/', admin.site.urls),
    
#     # API endpoints
#     path('api/floors/', include('apps.floors.urls')),
#     path('api/bookings/', include('apps.bookings.urls')),
#     path('api/sync/', include('apps.sync_offline.urls')),
    
#     # Authentication
#     path('api/auth/', include('dj_rest_auth.urls')),
#     path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
# ]

# # Serve media files in development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/floors/', include('apps.floors.urls')),
    path('api/bookings/', include('apps.bookings.urls')),
    path('api/sync/', include('apps.sync_offline.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    
    # Authentication
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/social/', include('allauth.socialaccount.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)