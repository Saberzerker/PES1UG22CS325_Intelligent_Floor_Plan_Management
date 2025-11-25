# """
# FEATURE 2: Offline Sync Service
# Handles batch synchronization of offline changes
# """

# from typing import Dict, List, Any
# from django.db import transaction
# from django.contrib.auth.models import User
# from apps.floors.models import FloorPlan, Room
# from apps.bookings.models import Booking
# from ..models import OfflineChange
# from apps.floors.services.conflict_resolution import ConflictResolutionService


# class OfflineSyncService:
#     """
#     Batch sync offline changes with conflict resolution
#     """
    
#     @staticmethod
#     def sync_batch(user: User, changes: List[Dict]) -> Dict[str, Any]:
#         """
#         Sync a batch of offline changes
        
#         Args:
#             user: User making the changes
#             changes: List of change dicts with:
#                 - change_type: 'CREATE' | 'UPDATE' | 'DELETE'
#                 - model_name: 'FloorPlan' | 'Room' | 'Booking'
#                 - object_id: int or None
#                 - change_data: dict of fields/values
#                 - version_at_change: int (for updates)
        
#         Returns:
#             {
#                 'synced': [...],
#                 'conflicts': [...],
#                 'failed': [...]
#             }
#         """
        
#         results = {
#             'synced': [],
#             'conflicts': [],
#             'failed': []
#         }
        
#         for change in changes:
#             try:
#                 with transaction.atomic():
#                     result = OfflineSyncService._sync_single_change(user, change)
#                     if result['status'] == 'synced':
#                         results['synced'].append(result)
#                     elif result['status'] == 'conflict':
#                         results['conflicts'].append(result)
#                     else:
#                         results['failed'].append(result)
                    
#                     # Mark the offline change as processed
#                     OfflineChange.objects.filter(
#                         user=user,
#                         change_type=change['change_type'],
#                         model_name=change['model_name'],
#                         object_id=change.get('object_id')
#                     ).update(sync_status='SYNCED')
                    
#             except Exception as e:
#                 results['failed'].append({
#                     'change': change,
#                     'error': str(e)
#                 })
        
#         return results
    
#     @staticmethod
#     def _sync_single_change(user: User, change: Dict) -> Dict[str, Any]:
#         """Sync a single change"""
#         change_type = change['change_type']
#         model_name = change['model_name']
#         object_id = change.get('object_id')
#         change_data = change['change_data']
#         version_at_change = change.get('version_at_change')
        
#         if model_name == 'FloorPlan':
#             return OfflineSyncService._sync_floor_plan(user, change_type, object_id, change_data, version_at_change)
#         elif model_name == 'Room':
#             return OfflineSyncService._sync_room(user, change_type, object_id, change_data)
#         elif model_name == 'Booking':
#             return OfflineSyncService._sync_booking(user, change_type, object_id, change_data)
        
#         return {
#             'status': 'failed',
#             'change': change,
#             'error': f'Unsupported model: {model_name}'
#         }
    
#     @staticmethod
#     def _sync_floor_plan(user: User, change_type: str, object_id: int, change_data: Dict, version_at_change: int) -> Dict[str, Any]:
#         """Sync FloorPlan changes with conflict detection"""
#         if change_type == 'CREATE':
#             floor_plan = FloorPlan.objects.create(
#                 created_by=user,
#                 updated_by=user,
#                 **change_data
#             )
#             return {
#                 'status': 'synced',
#                 'change': {'model_name': 'FloorPlan', 'object_id': floor_plan.id, 'change_type': 'CREATE'},
#                 'new_id': floor_plan.id
#             }
        
#         elif change_type == 'UPDATE':
#             floor_plan = FloorPlan.objects.select_for_update().get(id=object_id)
            
#             # Check version conflict
#             if version_at_change != floor_plan.version:
#                 # Try three-way merge
#                 base_data = {
#                     'name': floor_plan.name,
#                     'floor_number': floor_plan.floor_number,
#                 }
                
#                 merged_data, conflicts = ConflictResolutionService.three_way_merge(
#                     base_data, base_data, change_data
#                 )
                
#                 if conflicts:
#                     return {
#                         'status': 'conflict',
#                         'change': {'model_name': 'FloorPlan', 'object_id': object_id, 'change_type': 'UPDATE'},
#                         'conflicts': conflicts,
#                         'merged_data': merged_data
#                     }
                
#                 # Auto-merge
#                 for key, value in merged_data.items():
#                     setattr(floor_plan, key, value)
#                 floor_plan.version += 1
#                 floor_plan.save()
                
#                 return {
#                     'status': 'synced',
#                     'change': {'model_name': 'FloorPlan', 'object_id': object_id, 'change_type': 'UPDATE'},
#                     'strategy': 'THREE_WAY_MERGE_SUCCESS'
#                 }
            
#             # No conflict
#             for key, value in change_data.items():
#                 setattr(floor_plan, key, value)
#             floor_plan.version += 1
#             floor_plan.save()
            
#             return {
#                 'status': 'synced',
#                 'change': {'model_name': 'FloorPlan', 'object_id': object_id, 'change_type': 'UPDATE'}
#             }
        
#         elif change_type == 'DELETE':
#             FloorPlan.objects.filter(id=object_id).delete()
#             return {
#                 'status': 'synced',
#                 'change': {'model_name': 'FloorPlan', 'object_id': object_id, 'change_type': 'DELETE'}
#             }
        
#         return {
#             'status': 'failed',
#             'change': {'model_name': 'FloorPlan', 'object_id': object_id, 'change_type': change_type},
#             'error': f'Unsupported change type: {change_type}'
#         }
    
#     @staticmethod
#     def _sync_room(user: User, change_type: str, object_id: int, change_data: Dict) -> Dict[str, Any]:
#         """Sync Room changes"""
#         if change_type == 'CREATE':
#             room = Room.objects.create(**change_data)
#             return {
#                 'status': 'synced',
#                 'change': {'model_name': 'Room', 'object_id': room.id, 'change_type': 'CREATE'},
#                 'new_id': room.id
#             }
        
#         elif change_type == 'UPDATE':
#             room = Room.objects.get(id=object_id)
#             for key, value in change_data.items():
#                 setattr(room, key, value)
#             room.save()
#             return {
#                 'status': 'synced',
#                 'change': {'model_name': 'Room', 'object_id': object_id, 'change_type': 'UPDATE'}
#             }
        
#         elif change_type == 'DELETE':
#             Room.objects.filter(id=object_id).delete()
#             return {
#                 'status': 'synced',
#                 'change': {'model_name': 'Room', 'object_id': object_id, 'change_type': 'DELETE'}
#             }
        
#         return {
#             'status': 'failed',
#             'change': {'model_name': 'Room', 'object_id': object_id, 'change_type': change_type},
#             'error': f'Unsupported change type: {change_type}'
#         }
    
#     @staticmethod
#     def _sync_booking(user: User, change_type: str, object_id: int, change_data: Dict) -> Dict[str, Any]:
#         """Sync Booking changes"""
#         if change_type == 'CREATE':
#             change_data['user'] = user
#             booking = Booking.objects.create(**change_data)
#             return {
#                 'status': 'synced',
#                 'change': {'model_name': 'Booking', 'object_id': booking.id, 'change_type': 'CREATE'},
#                 'new_id': booking.id
#             }
        
#         elif change_type == 'UPDATE':
#             booking = Booking.objects.get(id=object_id, user=user)
#             for key, value in change_data.items():
#                 setattr(booking, key, value)
#             booking.save()
#             return {
#                 'status': 'synced',
#                 'change': {'model_name': 'Booking', 'object_id': object_id, 'change_type': 'UPDATE'}
#             }
        
#         elif change_type == 'DELETE':
#             Booking.objects.filter(id=object_id, user=user).delete()
#             return {
#                 'status': 'synced',
#                 'change': {'model_name': 'Booking', 'object_id': object_id, 'change_type': 'DELETE'}
#             }
        
#         return {
#             'status': 'failed',
#             'change': {'model_name': 'Booking', 'object_id': object_id, 'change_type': change_type},
#             'error': f'Unsupported change type: {change_type}'
#         }



"""
FEATURE 2: Offline Sync Service
Handles batch synchronization of offline changes
"""

from typing import Dict, List, Any
from django.db import transaction
from django.contrib.auth.models import User
from apps.floors.models import FloorPlan, Room
from apps.bookings.models import Booking
from ..models import OfflineChange
from apps.floors.services.conflict_resolution import ConflictResolutionService


class OfflineSyncService:
    """
    Batch sync offline changes with conflict resolution
    """
    
    @staticmethod
    def sync_batch(user: User, changes: List[Dict]) -> Dict[str, Any]:
        """
        Sync a batch of offline changes
        
        Args:
            user: User making the changes
            changes: List of change dicts with:
                - change_type: 'CREATE' | 'UPDATE' | 'DELETE'
                - model_name: 'FloorPlan' | 'Room' | 'Booking'
                - object_id: int or None
                - change_data: dict of fields/values
                - version_at_change: int (for updates)
        
        Returns:
            {
                'synced': [...],
                'conflicts': [...],
                'failed': [...]
            }
        """
        
        results = {
            'synced': [],
            'conflicts': [],
            'failed': []
        }
        
        for change in changes:
            try:
                with transaction.atomic():
                    result = OfflineSyncService._sync_single_change(user, change)
                    if result['status'] == 'synced':
                        results['synced'].append(result)
                    elif result['status'] == 'conflict':
                        results['conflicts'].append(result)
                    else:
                        results['failed'].append(result)
                    
                    # Mark the offline change as processed
                    OfflineChange.objects.filter(
                        user=user,
                        change_type=change['change_type'],
                        model_name=change['model_name'],
                        object_id=change.get('object_id')
                    ).update(sync_status='SYNCED')
                    
            except Exception as e:
                results['failed'].append({
                    'change': change,
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def _sync_single_change(user: User, change: Dict) -> Dict[str, Any]:
        """Sync a single change"""
        change_type = change['change_type']
        model_name = change['model_name']
        object_id = change.get('object_id')
        change_data = change['change_data']
        version_at_change = change.get('version_at_change')
        
        if model_name == 'FloorPlan':
            return OfflineSyncService._sync_floor_plan(user, change_type, object_id, change_data, version_at_change)
        elif model_name == 'Room':
            return OfflineSyncService._sync_room(user, change_type, object_id, change_data)
        elif model_name == 'Booking':
            return OfflineSyncService._sync_booking(user, change_type, object_id, change_data)
        
        return {
            'status': 'failed',
            'change': change,
            'error': f'Unsupported model: {model_name}'
        }
    
    @staticmethod
    def _sync_floor_plan(user: User, change_type: str, object_id: int, change_data: Dict, version_at_change: int) -> Dict[str, Any]:
        """Sync FloorPlan changes with conflict detection"""
        if change_type == 'CREATE':
            floor_plan = FloorPlan.objects.create(
                created_by=user,
                updated_by=user,
                **change_data
            )
            return {
                'status': 'synced',
                'change': {'model_name': 'FloorPlan', 'object_id': floor_plan.id, 'change_type': 'CREATE'},
                'new_id': floor_plan.id
            }
        
        elif change_type == 'UPDATE':
            floor_plan = FloorPlan.objects.select_for_update().get(id=object_id)
            
            # Check version conflict
            if version_at_change != floor_plan.version:
                # Try three-way merge
                base_data = {
                    'name': floor_plan.name,
                    'floor_number': floor_plan.floor_number,
                }
                
                merged_data, conflicts = ConflictResolutionService.three_way_merge(
                    base_data, base_data, change_data
                )
                
                if conflicts:
                    return {
                        'status': 'conflict',
                        'change': {'model_name': 'FloorPlan', 'object_id': object_id, 'change_type': 'UPDATE'},
                        'conflicts': conflicts,
                        'merged_data': merged_data
                    }
                
                # Auto-merge
                for key, value in merged_data.items():
                    setattr(floor_plan, key, value)
                floor_plan.version += 1
                floor_plan.save()
                
                return {
                    'status': 'synced',
                    'change': {'model_name': 'FloorPlan', 'object_id': object_id, 'change_type': 'UPDATE'},
                    'strategy': 'THREE_WAY_MERGE_SUCCESS'
                }
            
            # No conflict
            for key, value in change_data.items():
                setattr(floor_plan, key, value)
            floor_plan.version += 1
            floor_plan.save()
            
            return {
                'status': 'synced',
                'change': {'model_name': 'FloorPlan', 'object_id': object_id, 'change_type': 'UPDATE'}
            }
        
        elif change_type == 'DELETE':
            FloorPlan.objects.filter(id=object_id).delete()
            return {
                'status': 'synced',
                'change': {'model_name': 'FloorPlan', 'object_id': object_id, 'change_type': 'DELETE'}
            }
        
        return {
            'status': 'failed',
            'change': {'model_name': 'FloorPlan', 'object_id': object_id, 'change_type': change_type},
            'error': f'Unsupported change type: {change_type}'
        }
    
    @staticmethod
    def _sync_room(user: User, change_type: str, object_id: int, change_data: Dict) -> Dict[str, Any]:
        """Sync Room changes"""
        if change_type == 'CREATE':
            room = Room.objects.create(**change_data)
            return {
                'status': 'synced',
                'change': {'model_name': 'Room', 'object_id': room.id, 'change_type': 'CREATE'},
                'new_id': room.id
            }
        
        elif change_type == 'UPDATE':
            room = Room.objects.get(id=object_id)
            for key, value in change_data.items():
                setattr(room, key, value)
            room.save()
            return {
                'status': 'synced',
                'change': {'model_name': 'Room', 'object_id': object_id, 'change_type': 'UPDATE'}
            }
        
        elif change_type == 'DELETE':
            Room.objects.filter(id=object_id).delete()
            return {
                'status': 'synced',
                'change': {'model_name': 'Room', 'object_id': object_id, 'change_type': 'DELETE'}
            }
        
        return {
            'status': 'failed',
            'change': {'model_name': 'Room', 'object_id': object_id, 'change_type': change_type},
            'error': f'Unsupported change type: {change_type}'
        }
    
    @staticmethod
    def _sync_booking(user: User, change_type: str, object_id: int, change_data: Dict) -> Dict[str, Any]:
        """Sync Booking changes"""
        if change_type == 'CREATE':
            change_data['user'] = user
            booking = Booking.objects.create(**change_data)
            return {
                'status': 'synced',
                'change': {'model_name': 'Booking', 'object_id': booking.id, 'change_type': 'CREATE'},
                'new_id': booking.id
            }
        
        elif change_type == 'UPDATE':
            booking = Booking.objects.get(id=object_id, user=user)
            for key, value in change_data.items():
                setattr(booking, key, value)
            booking.save()
            return {
                'status': 'synced',
                'change': {'model_name': 'Booking', 'object_id': object_id, 'change_type': 'UPDATE'}
            }
        
        elif change_type == 'DELETE':
            Booking.objects.filter(id=object_id, user=user).delete()
            return {
                'status': 'synced',
                'change': {'model_name': 'Booking', 'object_id': object_id, 'change_type': 'DELETE'}
            }
        
        return {
            'status': 'failed',
            'change': {'model_name': 'Booking', 'object_id': object_id, 'change_type': change_type},
            'error': f'Unsupported change type: {change_type}'
        }