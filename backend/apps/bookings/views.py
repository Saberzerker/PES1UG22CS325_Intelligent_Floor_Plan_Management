"""Views for bookings app"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import datetime

from .models import Booking, UserRoomPreference
from .serializers import BookingSerializer, UserRoomPreferenceSerializer
from .services.recommendation_engine import RoomRecommendationEngine


class BookingViewSet(viewsets.ModelViewSet):
    """Bookings CRUD + room recommendations."""

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Admins see all bookings; employees see only their own."""
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def recommend(self, request):
        """FEATURE 3: Get room recommendations (open for demo)."""
        raw_participants = request.data.get("participants_count", 1)

        start_time_str = request.data.get("start_time")
        end_time_str = request.data.get("end_time")
        required_amenities = request.data.get("required_amenities", [])
        preferred_floor = request.data.get("preferred_floor")

        try:
            participants_count = int(raw_participants)
        except (TypeError, ValueError):
            return Response(
                {"error": "participants_count must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
        except Exception:
            return Response({"error": "Invalid datetime format"}, status=status.HTTP_400_BAD_REQUEST)

        # For demo, we allow anonymous recommend calls. In production you would
        # likely require authentication and pass the real user here.
        user = request.user if request.user and request.user.is_authenticated else None

        recommendations = RoomRecommendationEngine.recommend_rooms(
            user=user,
            participants_count=participants_count,
            start_time=start_time,
            end_time=end_time,
            required_amenities=required_amenities,
            preferred_floor=preferred_floor,
        )

        data = []
        for rec in recommendations:
            room_data = {
                "id": rec["room"].id,
                "name": rec["room"].name,
                "capacity": rec["room"].capacity,
                "floor_number": rec["room"].floor_plan.floor_number,
                "amenities": rec["room"].amenities_list,
                "score": rec["score"],
                "score_breakdown": rec["score_breakdown"],
            }
            data.append(room_data)

        return Response(data)


class UserRoomPreferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserRoomPreference.objects.all()
    serializer_class = UserRoomPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserRoomPreference.objects.filter(user=self.request.user)