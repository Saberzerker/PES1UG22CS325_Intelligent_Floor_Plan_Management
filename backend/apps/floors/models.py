# FloorPlan, Room, ConflictLog
"""
Floors app models: FloorPlan, Room, ConflictLog
"""

from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class FloorPlan(models.Model):
    """Floor plan with conflict detection via version tracking"""
    
    name = models.CharField(max_length=200)
    floor_number = models.IntegerField()
    image = models.ImageField(upload_to='floor_plans/%Y/%m/', null=True, blank=True)
    
    # FEATURE 1: Conflict Detection
    version = models.IntegerField(default=1)
    
    # Audit Trail
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_floor_plans')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_floor_plans')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)
    
    # FEATURE 1: Version History
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['floor_number']),
            models.Index(fields=['version']),
        ]
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
    
    @property
    def total_rooms(self):
        return self.rooms.count()


class Room(models.Model):
    """Individual room within a floor plan"""
    
    ROOM_TYPES = [
        ('MEETING', 'Meeting Room'),
        ('CONFERENCE', 'Conference Room'),
        ('HUDDLE', 'Huddle Space'),
        ('PHONE_BOOTH', 'Phone Booth'),
    ]
    
    floor_plan = models.ForeignKey(FloorPlan, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=200)
    room_number = models.CharField(max_length=50)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='MEETING')
    
    # FEATURE 3: Capacity & Location
    capacity = models.IntegerField()
    location_x = models.FloatField(default=0.0)
    location_y = models.FloatField(default=0.0)
    
    # FEATURE 3: Amenities
    has_projector = models.BooleanField(default=False)
    has_whiteboard = models.BooleanField(default=False)
    has_video_conference = models.BooleanField(default=False)
    has_tv_monitor = models.BooleanField(default=False)
    has_premium_audio = models.BooleanField(default=False)
    has_natural_light = models.BooleanField(default=False)
    has_kitchen_access = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    is_under_maintenance = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        unique_together = ['floor_plan', 'room_number']
        indexes = [
            models.Index(fields=['capacity']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} (Cap: {self.capacity})"
    
    @property
    def amenities_list(self):
        amenities = []
        if self.has_projector: amenities.append('Projector')
        if self.has_whiteboard: amenities.append('Whiteboard')
        if self.has_video_conference: amenities.append('Video Conference')
        if self.has_tv_monitor: amenities.append('TV/Monitor')
        if self.has_premium_audio: amenities.append('Premium Audio')
        if self.has_natural_light: amenities.append('Natural Light')
        if self.has_kitchen_access: amenities.append('Kitchen Access')
        return amenities


class ConflictLog(models.Model):
    """FEATURE 1: Track conflicts during simultaneous updates"""
    
    floor_plan = models.ForeignKey(FloorPlan, on_delete=models.CASCADE, related_name='conflicts')
    user_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='conflicts_as_user_a')
    user_b = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='conflicts_as_user_b')
    
    changes_a = models.JSONField()
    changes_b = models.JSONField()
    version_at_conflict = models.IntegerField()
    resolved_data = models.JSONField()
    resolution_strategy = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conflict: {self.floor_plan.name}"