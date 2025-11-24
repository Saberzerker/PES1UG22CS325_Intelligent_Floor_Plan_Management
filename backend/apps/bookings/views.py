# Views for bookings app
"""
Views for bookings app
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Booking, UserRoomPreference
from .serializers import BookingSerializer, UserRoomPreferenceSerializer
from apps.floors.models import Room


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by user if requested
        if self.request.query_params.get('my_bookings'):
            queryset = queryset.filter(user=user)
        
        # Filter by room
        room_id = self.request.query_params.get('room_id')
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_time__lte=end_date)
        
        return queryset.order_by('-start_time')
    
    @action(detail=False, methods=['post'])
    def recommend(self, request):
        """FEATURE 3: Recommend rooms based on requirements"""
        participants = int(request.data.get('participants_count', 1))
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        required_amenities = request.data.get('amenities', [])
        
        # Get all available rooms
        rooms = Room.objects.filter(
            is_active=True,
            is_under_maintenance=False,
            capacity__gte=participants
        )
        
        # Filter by amenities
        for amenity in required_amenities:
            if amenity == 'projector':
                rooms = rooms.filter(has_projector=True)
            elif amenity == 'whiteboard':
                rooms = rooms.filter(has_whiteboard=True)
            elif amenity == 'video_conference':
                rooms = rooms.filter(has_video_conference=True)
        
        # Check availability
        available_rooms = []
        for room in rooms:
            conflicts = Booking.objects.filter(
                room=room,
                status='CONFIRMED',
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if not conflicts.exists():
                available_rooms.append(room)
        
        # Score rooms based on user preference
        scored_rooms = []
        for room in available_rooms:
            score = 0
            
            # User preference score
            pref = UserRoomPreference.objects.filter(
                user=request.user,
                room=room
            ).first()
            if pref:
                score += pref.booking_count * 10
            
            # Capacity match score (prefer rooms close to required size)
            capacity_diff = abs(room.capacity - participants)
            score += max(0, 20 - capacity_diff)
            
            # Amenity bonus
            score += len(room.amenities_list) * 2
            
            scored_rooms.append({
                'room': room,
                'score': score
            })
        
        # Sort by score
        scored_rooms.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 5
        from apps.floors.serializers import RoomSerializer
        recommendations = [
            {
                **RoomSerializer(item['room']).data,
                'recommendation_score': item['score']
            }
            for item in scored_rooms[:5]
        ]
        
        return Response(recommendations)


class UserRoomPreferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserRoomPreference.objects.all()
    serializer_class = UserRoomPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)