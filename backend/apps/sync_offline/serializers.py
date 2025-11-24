# Serializers for sync app
"""
DRF Serializers for sync_offline app
"""

from rest_framework import serializers
from .models import OfflineChange


class OfflineChangeSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = OfflineChange
        fields = [
            'id', 'user', 'user_username', 'change_type', 'model_name',
            'object_id', 'change_data', 'original_state', 'version_at_change',
            'timestamp', 'sync_status', 'sync_attempts', 'synced_at',
            'sync_error', 'priority'
        ]
        read_only_fields = ['id', 'sync_attempts', 'synced_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)