from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import FloorPlan, Room, ConflictLog


@admin.register(FloorPlan)
class FloorPlanAdmin(SimpleHistoryAdmin):
    list_display = ['name', 'floor_number', 'version', 'created_by', 'updated_at', 'total_rooms']
    list_filter = ['floor_number', 'created_at']
    search_fields = ['name']
    readonly_fields = ['version', 'created_at', 'updated_at', 'total_rooms']


@admin.register(Room)
class RoomAdmin(SimpleHistoryAdmin):
    list_display = ['name', 'floor_plan', 'capacity', 'room_type', 'is_active']
    list_filter = ['room_type', 'floor_plan', 'is_active']
    search_fields = ['name', 'room_number']


@admin.register(ConflictLog)
class ConflictLogAdmin(admin.ModelAdmin):
    list_display = ['floor_plan', 'user_a', 'user_b', 'resolution_strategy', 'created_at']
    readonly_fields = ['floor_plan', 'user_a', 'user_b', 'changes_a', 'changes_b', 'resolved_data', 'resolution_strategy', 'created_at']