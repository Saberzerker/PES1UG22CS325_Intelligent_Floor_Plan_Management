# OfflineChange
"""
Sync Offline app models: OfflineChange
"""

from django.db import models
from django.contrib.auth.models import User


class OfflineChange(models.Model):
    """FEATURE 2: Store changes made offline for synchronization"""
    
    CHANGE_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]
    
    SYNC_STATUS = [
        ('PENDING', 'Pending'),
        ('SYNCED', 'Synced'),
        ('FAILED', 'Failed'),
        ('CONFLICT', 'Conflict'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    model_name = models.CharField(max_length=50)
    object_id = models.IntegerField(null=True, blank=True)
    change_data = models.JSONField()
    original_state = models.JSONField(null=True, blank=True)
    version_at_change = models.IntegerField(null=True, blank=True)
    
    timestamp = models.DateTimeField()
    sync_status = models.CharField(max_length=20, choices=SYNC_STATUS, default='PENDING')
    sync_attempts = models.IntegerField(default=0)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_error = models.TextField(blank=True)
    priority = models.IntegerField(default=5)
    
    class Meta:
        ordering = ['priority', 'timestamp']
        indexes = [
            models.Index(fields=['sync_status', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.change_type} {self.model_name} - {self.sync_status}"