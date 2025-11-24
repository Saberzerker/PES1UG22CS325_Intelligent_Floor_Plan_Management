# Views for sync app
"""
Views for sync_offline app
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import OfflineChange
from .serializers import OfflineChangeSerializer


class OfflineChangeViewSet(viewsets.ModelViewSet):
    queryset = OfflineChange.objects.all()
    serializer_class = OfflineChangeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """FEATURE 2: Sync offline changes"""
        changes_data = request.data.get('changes', [])
        results = []
        
        for change_data in changes_data:
            # Create offline change record
            serializer = self.get_serializer(data=change_data)
            if serializer.is_valid():
                offline_change = serializer.save()
                
                # Try to apply the change
                try:
                    # TODO: Implement actual sync logic based on model_name
                    offline_change.sync_status = 'SYNCED'
                    offline_change.synced_at = timezone.now()
                    offline_change.save()
                    results.append({
                        'id': offline_change.id,
                        'status': 'synced'
                    })
                except Exception as e:
                    offline_change.sync_status = 'FAILED'
                    offline_change.sync_error = str(e)
                    offline_change.sync_attempts += 1
                    offline_change.save()
                    results.append({
                        'id': offline_change.id,
                        'status': 'failed',
                        'error': str(e)
                    })
            else:
                results.append({
                    'status': 'invalid',
                    'errors': serializer.errors
                })
        
        return Response({'results': results})
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending changes"""
        pending = self.get_queryset().filter(sync_status='PENDING')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)