"""
Analytics views for dashboard metrics
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from apps.floors.models import FloorPlan, Room
from apps.bookings.models import Booking
from apps.floors.models import ConflictLog


class DashboardAnalyticsView(APIView):
    """
    Analytics endpoint for dashboard metrics
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard metrics"""
        user = request.user
        now = timezone.now()
        today = now.date()
        
        if user.is_staff:
            # Admin metrics
            metrics = {
                'rooms_booked': Booking.objects.filter(status='CONFIRMED').count(),
                'bookings_today': Booking.objects.filter(
                    start_time__date=today, status='CONFIRMED'
                ).count(),
                'conflicts_pending': ConflictLog.objects.filter(
                    manually_resolved_by__isnull=True
                ).count(),
                'active_meetings': Booking.objects.filter(
                    start_time__lte=now,
                    end_time__gte=now,
                    status='CONFIRMED'
                ).count(),
            }
        else:
            # Employee metrics
            metrics = {
                'meetings_booked': Booking.objects.filter(
                    user=user, status='CONFIRMED'
                ).count(),
                'available_rooms': Room.objects.filter(
                    is_active=True, is_under_maintenance=False
                ).count(),
            }
        
        return Response(metrics)