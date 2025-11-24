"""
WebSocket routing for floors app
"""

from django.urls import re_path
from .consumers import FloorPlanConsumer, NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/floor-plans/(?P<floor_plan_id>\w+)/$', FloorPlanConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]