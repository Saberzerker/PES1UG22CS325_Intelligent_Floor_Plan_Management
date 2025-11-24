# Serializers for bookings app
"""
DRF Serializers for bookings app
"""

from rest_framework import serializers
from .models import Booking, UserRoomPreference
from apps.floors.models import Room


class BookingSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'room', 'room_name', 'user', 'user_username',
            'start_time', 'end_time', 'participants_count',
            'purpose', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        # Check for overlapping bookings
        room = data.get('room')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time")
        
        # Check for conflicts
        overlapping = Booking.objects.filter(
            room=room,
            status='CONFIRMED',
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        # Exclude current booking if updating
        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)
        
        if overlapping.exists():
            raise serializers.ValidationError("This room is already booked for the selected time")
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserRoomPreferenceSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserRoomPreference
        fields = ['id', 'user', 'user_username', 'room', 'room_name', 'booking_count', 'last_booked']
        read_only_fields = ['id', 'booking_count', 'last_booked']