# Booking, UserPreference
"""
Bookings app models: Booking, UserRoomPreference
"""

from django.db import models
from django.contrib.auth.models import User
from apps.floors.models import Room


class Booking(models.Model):
    """FEATURE 3: Room booking records"""
    
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants_count = models.IntegerField()
    purpose = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['room', 'start_time', 'end_time']),
        ]
    
    def __str__(self):
        return f"{self.room.name} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update user preference on new booking
        if is_new and self.status == 'CONFIRMED':
            pref, created = UserRoomPreference.objects.get_or_create(
                user=self.user,
                room=self.room,
                defaults={'booking_count': 0}
            )
            pref.booking_count += 1
            pref.save()


class UserRoomPreference(models.Model):
    """FEATURE 3: Track user booking history for recommendations"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booking_count = models.IntegerField(default=0)
    last_booked = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'room']
        ordering = ['-booking_count']
    
    def __str__(self):
        return f"{self.user.username} → {self.room.name} ({self.booking_count}x)"