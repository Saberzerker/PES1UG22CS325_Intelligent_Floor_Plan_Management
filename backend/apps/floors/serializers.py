# Serializers for floors app
"""
DRF Serializers for floors app
"""

from rest_framework import serializers
from .models import FloorPlan, Room, ConflictLog
from django.contrib.auth.models import User


class RoomSerializer(serializers.ModelSerializer):
    amenities = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'floor_plan', 'name', 'room_number', 'room_type',
            'capacity', 'location_x', 'location_y',
            'has_projector', 'has_whiteboard', 'has_video_conference',
            'has_tv_monitor', 'has_premium_audio', 'has_natural_light',
            'has_kitchen_access', 'is_active', 'is_under_maintenance',
            'amenities', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_amenities(self, obj):
        return obj.amenities_list


class FloorPlanSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = FloorPlan
        fields = [
            'id', 'name', 'floor_number', 'image', 'version',
            'created_by', 'created_by_username', 'updated_by', 'updated_by_username',
            'created_at', 'updated_at', 'is_active', 'rooms', 'total_rooms'
        ]
        read_only_fields = ['id', 'version', 'created_at', 'updated_at', 'total_rooms']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # FEATURE 1: Increment version on update
        instance.version += 1
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class ConflictLogSerializer(serializers.ModelSerializer):
    floor_plan_name = serializers.CharField(source='floor_plan.name', read_only=True)
    user_a_username = serializers.CharField(source='user_a.username', read_only=True)
    user_b_username = serializers.CharField(source='user_b.username', read_only=True)
    
    class Meta:
        model = ConflictLog
        fields = [
            'id', 'floor_plan', 'floor_plan_name',
            'user_a', 'user_a_username', 'user_b', 'user_b_username',
            'changes_a', 'changes_b', 'version_at_conflict',
            'resolved_data', 'resolution_strategy', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']