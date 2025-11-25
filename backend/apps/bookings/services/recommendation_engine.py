# # FEATURE 3 - Room recommendation engine
# """
# FEATURE 3: AI-Powered Room Recommendation Engine
# Recommends best rooms based on user preferences and meeting requirements
# """

# from typing import List, Dict, Any
# from django.contrib.auth.models import User
# from django.db.models import Q, Count
# from django.utils import timezone
# from datetime import datetime, timedelta
# from apps.floors.models import Room
# from ..models import Booking, UserRoomPreference


# class RoomRecommendationEngine:
#     """
#     Smart recommendation system for meeting rooms
#     """
    
#     # Scoring weights
#     WEIGHT_USER_PREFERENCE = 10
#     WEIGHT_CAPACITY_MATCH = 20
#     WEIGHT_AMENITIES = 5
#     WEIGHT_RECENT_USAGE = 3
#     WEIGHT_PROXIMITY = 2
    
#     @classmethod
#     def recommend_rooms(
#         cls,
#         user: User,
#         participants_count: int,
#         start_time: datetime,
#         end_time: datetime,
#         required_amenities: List[str] = None,
#         preferred_floor: int = None
#     ) -> List[Dict[str, Any]]:
#         """
#         Main recommendation method
#         Returns list of rooms sorted by recommendation score
#         """
#         required_amenities = required_amenities or []
        
#         # Step 1: Get available rooms
#         available_rooms = cls._get_available_rooms(
#             participants_count,
#             start_time,
#             end_time,
#             required_amenities
#         )
        
#         # Step 2: Score each room
#         scored_rooms = []
#         for room in available_rooms:
#             score = cls._calculate_room_score(
#                 room,
#                 user,
#                 participants_count,
#                 required_amenities,
#                 preferred_floor
#             )
            
#             scored_rooms.append({
#                 'room': room,
#                 'score': score,
#                 'score_breakdown': cls._get_score_breakdown(
#                     room,
#                     user,
#                     participants_count,
#                     required_amenities,
#                     preferred_floor
#                 )
#             })
        
#         # Step 3: Sort by score
#         scored_rooms.sort(key=lambda x: x['score'], reverse=True)
        
#         return scored_rooms[:5]  # Top 5 recommendations
    
#     @staticmethod
#     def _get_available_rooms(
#         min_capacity: int,
#         start_time: datetime,
#         end_time: datetime,
#         required_amenities: List[str]
#     ) -> List[Room]:
#         """
#         Filter rooms by availability and basic requirements
#         """
#         # Base filters
#         rooms = Room.objects.filter(
#             is_active=True,
#             is_under_maintenance=False,
#             capacity__gte=min_capacity
#         )
        
#         # Filter by amenities
#         for amenity in required_amenities:
#             if amenity == 'projector':
#                 rooms = rooms.filter(has_projector=True)
#             elif amenity == 'whiteboard':
#                 rooms = rooms.filter(has_whiteboard=True)
#             elif amenity == 'video_conference':
#                 rooms = rooms.filter(has_video_conference=True)
#             elif amenity == 'tv_monitor':
#                 rooms = rooms.filter(has_tv_monitor=True)
#             elif amenity == 'premium_audio':
#                 rooms = rooms.filter(has_premium_audio=True)
#             elif amenity == 'natural_light':
#                 rooms = rooms.filter(has_natural_light=True)
#             elif amenity == 'kitchen_access':
#                 rooms = rooms.filter(has_kitchen_access=True)
        
#         # Check availability (no overlapping bookings)
#         available = []
#         for room in rooms:
#             conflicts = Booking.objects.filter(
#                 room=room,
#                 status='CONFIRMED',
#                 start_time__lt=end_time,
#                 end_time__gt=start_time
#             )
#             if not conflicts.exists():
#                 available.append(room)
        
#         return available
    
#     @classmethod
#     def _calculate_room_score(
#         cls,
#         room: Room,
#         user: User,
#         participants_count: int,
#         required_amenities: List[str],
#         preferred_floor: int = None
#     ) -> float:
#         """
#         Calculate total recommendation score for a room
#         """
#         score = 0.0
        
#         # 1. User preference score
#         pref = UserRoomPreference.objects.filter(user=user, room=room).first()
#         if pref:
#             score += pref.booking_count * cls.WEIGHT_USER_PREFERENCE
        
#         # 2. Capacity match score (prefer rooms close to required size)
#         capacity_diff = abs(room.capacity - participants_count)
#         capacity_score = max(0, 10 - capacity_diff)  # Max 10 points
#         score += capacity_score * cls.WEIGHT_CAPACITY_MATCH
        
#         # 3. Amenities score
#         amenity_count = len(room.amenities_list)
#         score += amenity_count * cls.WEIGHT_AMENITIES
        
#         # 4. Recent usage score (rooms used recently get slight penalty to distribute usage)
#         recent_bookings = Booking.objects.filter(
#             room=room,
#             start_time__gte=timezone.now() - timedelta(days=7)
#         ).count()
#         score -= recent_bookings * cls.WEIGHT_RECENT_USAGE
        
#         # 5. Floor preference score
#         if preferred_floor and room.floor_plan.floor_number == preferred_floor:
#             score += 15
        
#         return max(score, 0)  # Ensure non-negative
    
#     @classmethod
#     def _get_score_breakdown(
#         cls,
#         room: Room,
#         user: User,
#         participants_count: int,
#         required_amenities: List[str],
#         preferred_floor: int = None
#     ) -> Dict[str, float]:
#         """
#         Get detailed breakdown of recommendation score
#         """
#         breakdown = {}
        
#         # User preference
#         pref = UserRoomPreference.objects.filter(user=user, room=room).first()
#         breakdown['user_preference'] = pref.booking_count * cls.WEIGHT_USER_PREFERENCE if pref else 0
        
#         # Capacity match
#         capacity_diff = abs(room.capacity - participants_count)
#         capacity_score = max(0, 10 - capacity_diff)
#         breakdown['capacity_match'] = capacity_score * cls.WEIGHT_CAPACITY_MATCH
        
#         # Amenities
#         breakdown['amenities'] = len(room.amenities_list) * cls.WEIGHT_AMENITIES
        
#         # Recent usage
#         recent_bookings = Booking.objects.filter(
#             room=room,
#             start_time__gte=timezone.now() - timedelta(days=7)
#         ).count()
#         breakdown['recent_usage_penalty'] = -recent_bookings * cls.WEIGHT_RECENT_USAGE
        
#         # Floor preference
#         if preferred_floor and room.floor_plan.floor_number == preferred_floor:
#             breakdown['floor_preference'] = 15
#         else:
#             breakdown['floor_preference'] = 0
        
#         breakdown['total'] = sum(breakdown.values())
        
#         return breakdown

"""
FEATURE 3: AI-Powered Room Recommendation Engine
Recommends best rooms based on user preferences and meeting requirements
"""

from typing import List, Dict, Any
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from apps.floors.models import Room
from ..models import Booking, UserRoomPreference


class RoomRecommendationEngine:
    """
    Smart recommendation system for meeting rooms
    """
    
    # Scoring weights
    WEIGHT_USER_PREFERENCE = 10
    WEIGHT_CAPACITY_MATCH = 20
    WEIGHT_AMENITIES = 5
    WEIGHT_RECENT_USAGE = 3
    WEIGHT_PROXIMITY = 2
    
    @classmethod
    def recommend_rooms(
        cls,
        user: User,
        participants_count: int,
        start_time: datetime,
        end_time: datetime,
        required_amenities: List[str] = None,
        preferred_floor: int = None
    ) -> List[Dict[str, Any]]:
        """
        Main recommendation method
        Returns list of rooms sorted by recommendation score
        """
        required_amenities = required_amenities or []
        
        # Step 1: Get available rooms
        available_rooms = cls._get_available_rooms(
            participants_count,
            start_time,
            end_time,
            required_amenities
        )
        
        # Step 2: Score each room
        scored_rooms = []
        for room in available_rooms:
            score = cls._calculate_room_score(
                room,
                user,
                participants_count,
                required_amenities,
                preferred_floor
            )
            
            scored_rooms.append({
                'room': room,
                'score': score,
                'score_breakdown': cls._get_score_breakdown(
                    room,
                    user,
                    participants_count,
                    required_amenities,
                    preferred_floor
                )
            })
        
        # Step 3: Sort by score
        scored_rooms.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_rooms[:5]  # Top 5 recommendations
    
    @staticmethod
    def _get_available_rooms(
        min_capacity: int,
        start_time: datetime,
        end_time: datetime,
        required_amenities: List[str]
    ) -> List[Room]:
        """
        Filter rooms by availability and basic requirements
        """
        # Base filters
        rooms = Room.objects.filter(
            is_active=True,
            is_under_maintenance=False,
            capacity__gte=min_capacity
        )
        
        # Filter by amenities
        for amenity in required_amenities:
            if amenity == 'projector':
                rooms = rooms.filter(has_projector=True)
            elif amenity == 'whiteboard':
                rooms = rooms.filter(has_whiteboard=True)
            elif amenity == 'video_conference':
                rooms = rooms.filter(has_video_conference=True)
            elif amenity == 'tv_monitor':
                rooms = rooms.filter(has_tv_monitor=True)
            elif amenity == 'premium_audio':
                rooms = rooms.filter(has_premium_audio=True)
            elif amenity == 'natural_light':
                rooms = rooms.filter(has_natural_light=True)
            elif amenity == 'kitchen_access':
                rooms = rooms.filter(has_kitchen_access=True)
        
        # Check availability (no overlapping bookings)
        available = []
        for room in rooms:
            conflicts = Booking.objects.filter(
                room=room,
                status='CONFIRMED',
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if not conflicts.exists():
                available.append(room)
        
        return available
    
    @classmethod
    def _calculate_room_score(
        cls,
        room: Room,
        user: User,
        participants_count: int,
        required_amenities: List[str],
        preferred_floor: int = None
    ) -> float:
        """
        Calculate total recommendation score for a room
        """
        score = 0.0
        
        # 1. User preference score
        pref = UserRoomPreference.objects.filter(user=user, room=room).first()
        if pref:
            score += pref.booking_count * cls.WEIGHT_USER_PREFERENCE
        
        # 2. Capacity match score (prefer rooms close to required size)
        capacity_diff = abs(room.capacity - participants_count)
        capacity_score = max(0, 10 - capacity_diff)  # Max 10 points
        score += capacity_score * cls.WEIGHT_CAPACITY_MATCH
        
        # 3. Amenities score
        amenity_count = len(room.amenities_list)
        score += amenity_count * cls.WEIGHT_AMENITIES
        
        # 4. Recent usage score (rooms used recently get slight penalty to distribute usage)
        recent_bookings = Booking.objects.filter(
            room=room,
            start_time__gte=timezone.now() - timedelta(days=7)
        ).count()
        score -= recent_bookings * cls.WEIGHT_RECENT_USAGE
        
        # 5. Floor preference score
        if preferred_floor and room.floor_plan.floor_number == preferred_floor:
            score += 15
        
        return max(score, 0)  # Ensure non-negative
    
    @classmethod
    def _get_score_breakdown(
        cls,
        room: Room,
        user: User,
        participants_count: int,
        required_amenities: List[str],
        preferred_floor: int = None
    ) -> Dict[str, float]:
        """
        Get detailed breakdown of recommendation score
        """
        breakdown = {}
        
        # User preference
        pref = UserRoomPreference.objects.filter(user=user, room=room).first()
        breakdown['user_preference'] = pref.booking_count * cls.WEIGHT_USER_PREFERENCE if pref else 0
        
        # Capacity match
        capacity_diff = abs(room.capacity - participants_count)
        capacity_score = max(0, 10 - capacity_diff)
        breakdown['capacity_match'] = capacity_score * cls.WEIGHT_CAPACITY_MATCH
        
        # Amenities
        breakdown['amenities'] = len(room.amenities_list) * cls.WEIGHT_AMENITIES
        
        # Recent usage
        recent_bookings = Booking.objects.filter(
            room=room,
            start_time__gte=timezone.now() - timedelta(days=7)
        ).count()
        breakdown['recent_usage_penalty'] = -recent_bookings * cls.WEIGHT_RECENT_USAGE
        
        # Floor preference
        if preferred_floor and room.floor_plan.floor_number == preferred_floor:
            breakdown['floor_preference'] = 15
        else:
            breakdown['floor_preference'] = 0
        
        breakdown['total'] = sum(breakdown.values())
        
        return breakdown