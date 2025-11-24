"""
Views for floors app - Updated with conflict resolution
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db import transaction
from .models import FloorPlan, Room, ConflictLog
from .serializers import FloorPlanSerializer, RoomSerializer, ConflictLogSerializer
from .services.conflict_resolution import ConflictResolutionService


class FloorPlanViewSet(viewsets.ModelViewSet):
    queryset = FloorPlan.objects.filter(is_active=True)
    serializer_class = FloorPlanSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get version history of a floor plan"""
        floor_plan = self.get_object()
        history = floor_plan.history.all()
        data = [{
            'version': h.version,
            'updated_by': h.updated_by.username if h.updated_by else None,
            'updated_at': h.history_date,
            'change_type': h.history_type,
        } for h in history]
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def detect_conflict(self, request, pk=None):
        """FEATURE 1: Detect if there's a conflict before saving"""
        floor_plan = self.get_object()
        client_version = request.data.get('version')
        
        if int(client_version) < floor_plan.version:
            return Response({
                'conflict': True,
                'server_version': floor_plan.version,
                'client_version': client_version,
                'message': 'Floor plan has been updated by another user'
            }, status=status.HTTP_409_CONFLICT)
        
        return Response({'conflict': False})
    
    def update(self, request, *args, **kwargs):
        """FEATURE 1: Override update to handle conflicts"""
        floor_plan = self.get_object()
        client_version = request.data.get('version', floor_plan.version)
        
        with transaction.atomic():
            # Check for conflict
            if ConflictResolutionService.detect_conflict(floor_plan, client_version):
                # Attempt three-way merge
                base_data = {
                    'name': floor_plan.name,
                    'floor_number': floor_plan.floor_number,
                }
                
                theirs_data = {
                    'name': request.data.get('name', floor_plan.name),
                    'floor_number': request.data.get('floor_number', floor_plan.floor_number),
                }
                
                # Get last history as base
                history = floor_plan.history.all()
                if history.count() > 1:
                    base_version = history[1]
                    base_data = {
                        'name': base_version.name,
                        'floor_number': base_version.floor_number,
                    }
                
                merged_data, conflicts = ConflictResolutionService.three_way_merge(
                    base_data, base_data, theirs_data  # User A is current, User B is theirs
                )
                
                if conflicts:
                    # Log conflict and return 409
                    ConflictLog.objects.create(
                        floor_plan=floor_plan,
                        user_a=request.user,
                        user_b=floor_plan.updated_by or floor_plan.created_by,
                        changes_a=base_data,
                        changes_b=theirs_data,
                        resolved_data=merged_data,
                        resolution_strategy='THREE_WAY_MERGE_AUTO'
                    )
                    
                    return Response({
                        'error': 'CONFLICT_DETECTED',
                        'expected_version': floor_plan.version,
                        'current_version': floor_plan.version,
                        'conflicts': conflicts,
                        'merged_data': merged_data
                    }, status=status.HTTP_409_CONFLICT)
                
                # Auto-merge successful
                for key, value in merged_data.items():
                    setattr(floor_plan, key, value)
                floor_plan.version += 1
                floor_plan.save()
                
                serializer = self.get_serializer(floor_plan)
                return Response(serializer.data)
            
            # No conflict, proceed normally
            return super().update(request, *args, **kwargs)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(is_active=True)
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def by_floor(self, request):
        """Get rooms for a specific floor plan"""
        floor_plan_id = request.query_params.get('floor_plan_id')
        if not floor_plan_id:
            return Response({'error': 'floor_plan_id required'}, status=400)
        
        rooms = self.queryset.filter(floor_plan_id=floor_plan_id)
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)


class ConflictLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConflictLog.objects.all()
    serializer_class = ConflictLogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]