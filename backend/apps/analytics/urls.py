"""
URL routing for analytics app
"""

from django.urls import path
from .views import DashboardAnalyticsView

urlpatterns = [
    path('dashboard/', DashboardAnalyticsView.as_view(), name='dashboard-analytics'),
]