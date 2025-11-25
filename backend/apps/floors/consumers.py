# # WebSocket consumer
# """
# WebSocket consumers for real-time updates
# """

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.contrib.auth.models import User
# from .models import FloorPlan


# class FloorPlanConsumer(AsyncWebsocketConsumer):
#     """
#     WebSocket consumer for real-time floor plan updates
#     """
    
#     async def connect(self):
#         """Join floor plan room group"""
#         self.floor_plan_id = self.scope['url_route']['kwargs']['floor_plan_id']
#         self.room_group_name = f'floor_plan_{self.floor_plan_id}'
        
#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
        
#         await self.accept()
    
#     async def disconnect(self, close_code):
#         """Leave room group"""
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
    
#     async def receive(self, text_data):
#         """Receive message from WebSocket"""
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
        
#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'floor_plan_update',
#                 'message': message
#             }
#         )
    
#     async def floor_plan_update(self, event):
#         """Receive message from room group"""
#         message = event['message']
        
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))


# class NotificationConsumer(AsyncWebsocketConsumer):
#     """
#     WebSocket consumer for user notifications
#     """
    
#     async def connect(self):
#         """Join user notification group"""
#         self.user_id = self.scope['user'].id if self.scope['user'].is_authenticated else None
        
#         if self.user_id:
#             self.room_group_name = f'user_{self.user_id}'
            
#             await self.channel_layer.group_add(
#                 self.room_group_name,
#                 self.channel_name
#             )
            
#             await self.accept()
#         else:
#             await self.close()
    
#     async def disconnect(self, close_code):
#         """Leave room group"""
#         if hasattr(self, 'room_group_name'):
#             await self.channel_layer.group_discard(
#                 self.room_group_name,
#                 self.channel_name
#             )
    
#     async def receive(self, text_data):
#         """Receive message from WebSocket"""
#         # For now, just acknowledge
#         await self.send(text_data=json.dumps({
#             'message': 'Message received'
#         }))
    
#     async def notification_update(self, event):
#         """Receive notification from room group"""
#         notification = event['notification']
        
#         # Send notification to WebSocket
#         await self.send(text_data=json.dumps({
#             'type': 'notification',
#             'data': notification
#         }))

"""
WebSocket consumers for real-time updates
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import FloorPlan


class FloorPlanConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time floor plan updates
    """
    
    async def connect(self):
        """Join floor plan room group"""
        self.floor_plan_id = self.scope['url_route']['kwargs']['floor_plan_id']
        self.room_group_name = f'floor_plan_{self.floor_plan_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Leave room group"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'floor_plan_update',
                'message': message
            }
        )
    
    async def floor_plan_update(self, event):
        """Receive message from room group"""
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for user notifications
    """
    
    async def connect(self):
        """Join user notification group"""
        self.user_id = self.scope['user'].id if self.scope['user'].is_authenticated else None
        
        if self.user_id:
            self.room_group_name = f'user_{self.user_id}'
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Leave room group"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        # For now, just acknowledge
        await self.send(text_data=json.dumps({
            'message': 'Message received'
        }))
    
    async def notification_update(self, event):
        """Receive notification from room group"""
        notification = event['notification']
        
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': notification
        }))