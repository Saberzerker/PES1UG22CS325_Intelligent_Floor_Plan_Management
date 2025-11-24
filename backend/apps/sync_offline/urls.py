"""
URL routing for sync_offline app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfflineChangeViewSet

router = DefaultRouter()
router.register(r'offline-changes', OfflineChangeViewSet, basename='offlinechange')

urlpatterns = [
    path('', include(router.urls)),
]