# FEATURE 1B - Conflict resolution
"""
FEATURE 1: Intelligent Conflict Resolution Service
Handles concurrent edits to floor plans using different merge strategies
"""

from typing import Dict, List, Any, Tuple
from django.contrib.auth.models import User
from ..models import FloorPlan, Room, ConflictLog
import json


class ConflictResolutionService:
    """
    Resolves conflicts when multiple users edit the same floor plan simultaneously
    """
    
    STRATEGY_LAST_WRITE_WINS = 'LAST_WRITE_WINS'
    STRATEGY_FIELD_LEVEL_MERGE = 'FIELD_LEVEL_MERGE'
    STRATEGY_MANUAL = 'MANUAL'
    STRATEGY_THREE_WAY_MERGE = 'THREE_WAY_MERGE'
    
    @staticmethod
    def detect_conflict(floor_plan: FloorPlan, client_version: int) -> bool:
        """
        Check if there's a version conflict
        """
        return floor_plan.version > client_version
    
    @staticmethod
    def three_way_merge(
        base_data: Dict,
        user_a_data: Dict,
        user_b_data: Dict
    ) -> Tuple[Dict, List[str]]:
        """
        Perform three-way merge (like Git merge)
        Returns: (merged_data, conflicts)
        """
        merged = {}
        conflicts = []
        
        all_keys = set(base_data.keys()) | set(user_a_data.keys()) | set(user_b_data.keys())
        
        for key in all_keys:
            base_val = base_data.get(key)
            a_val = user_a_data.get(key)
            b_val = user_b_data.get(key)
            
            # If both users made the same change
            if a_val == b_val:
                merged[key] = a_val
            
            # If only user A changed it
            elif a_val != base_val and b_val == base_val:
                merged[key] = a_val
            
            # If only user B changed it
            elif b_val != base_val and a_val == base_val:
                merged[key] = b_val
            
            # CONFLICT: Both users changed the same field differently
            elif a_val != b_val and a_val != base_val and b_val != base_val:
                conflicts.append(key)
                # Default to user B (last write wins for this field)
                merged[key] = b_val
            
            else:
                merged[key] = base_val
        
        return merged, conflicts
    
    @staticmethod
    def field_level_merge(
        original_data: Dict,
        changes_a: Dict,
        changes_b: Dict
    ) -> Dict:
        """
        Merge changes at field level - non-overlapping fields are merged
        """
        merged = original_data.copy()
        
        # Apply changes from user A
        for key, value in changes_a.items():
            merged[key] = value
        
        # Apply changes from user B (overwrites conflicts)
        for key, value in changes_b.items():
            merged[key] = value
        
        return merged
    
    @classmethod
    def resolve_conflict(
        cls,
        floor_plan: FloorPlan,
        user_a: User,
        user_b: User,
        changes_a: Dict,
        changes_b: Dict,
        strategy: str = STRATEGY_THREE_WAY_MERGE
    ) -> Dict[str, Any]:
        """
        Main conflict resolution method
        """
        # Get base version (from history)
        history = floor_plan.history.all()
        base_version = None
        if history.count() > 1:
            base_version = history[1]  # Previous version
        
        base_data = {
            'name': base_version.name if base_version else floor_plan.name,
            'floor_number': base_version.floor_number if base_version else floor_plan.floor_number,
        }
        
        resolved_data = {}
        conflict_fields = []
        
        if strategy == cls.STRATEGY_LAST_WRITE_WINS:
            # Simply use the latest changes (user B)
            resolved_data = changes_b
        
        elif strategy == cls.STRATEGY_FIELD_LEVEL_MERGE:
            # Merge non-overlapping changes
            resolved_data = cls.field_level_merge(base_data, changes_a, changes_b)
        
        elif strategy == cls.STRATEGY_THREE_WAY_MERGE:
            # Smart merge like Git
            resolved_data, conflict_fields = cls.three_way_merge(
                base_data,
                changes_a,
                changes_b
            )
        
        # Log the conflict
        conflict_log = ConflictLog.objects.create(
            floor_plan=floor_plan,
            user_a=user_a,
            user_b=user_b,
            changes_a=changes_a,
            changes_b=changes_b,
            version_at_conflict=floor_plan.version,
            resolved_data=resolved_data,
            resolution_strategy=strategy
        )
        
        return {
            'resolved_data': resolved_data,
            'conflict_fields': conflict_fields,
            'strategy_used': strategy,
            'conflict_log_id': conflict_log.id
        }
    
    @staticmethod
    def get_conflict_suggestions(
        floor_plan: FloorPlan,
        proposed_changes: Dict
    ) -> List[Dict]:
        """
        Suggest potential conflicts before user saves
        """
        suggestions = []
        
        # Check recent history
        recent_changes = floor_plan.history.filter(
            history_date__gte=floor_plan.updated_at
        )
        
        for change in recent_changes:
            overlapping_fields = set(proposed_changes.keys()) & set(change.history_change_reason or {})
            if overlapping_fields:
                suggestions.append({
                    'user': change.history_user.username if change.history_user else 'Unknown',
                    'timestamp': change.history_date,
                    'conflicting_fields': list(overlapping_fields)
                })
        
        return suggestions