# Views for floors app
"""
Views for floors app
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import FloorPlan, Room, ConflictLog
from .serializers import FloorPlanSerializer, RoomSerializer, ConflictLogSerializer


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