# """
# URL routing for bookings app
# """

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import BookingViewSet, UserRoomPreferenceViewSet

# router = DefaultRouter()
# router.register(r'bookings', BookingViewSet, basename='booking')
# router.register(r'preferences', UserRoomPreferenceViewSet, basename='preference')

# urlpatterns = [
#     path('', include(router.urls)),
# ]

"""
URL routing for bookings app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, UserRoomPreferenceViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'preferences', UserRoomPreferenceViewSet, basename='preference')

urlpatterns = [
    path('', include(router.urls)),
]