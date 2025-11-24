"""
URL routing for floors app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FloorPlanViewSet, RoomViewSet, ConflictLogViewSet

router = DefaultRouter()
router.register(r'floor-plans', FloorPlanViewSet, basename='floorplan')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'conflicts', ConflictLogViewSet, basename='conflictlog')

urlpatterns = [
    path('', include(router.urls)),
]