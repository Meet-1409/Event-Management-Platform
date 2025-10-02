import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from datetime import datetime
from .models import AdvancedChatRoom, AdvancedChatMessage

User = get_user_model()

class AdvancedChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'advanced_chat_{self.room_id}'
        self.user = self.scope['user']

        # Accept the connection first
        await self.accept()
        
        # Then verify access
        has_access = await self._verify_room_access()
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def _verify_room_access(self):
        try:
            room = AdvancedChatRoom.objects.get(id=self.room_id)
            return room.participants.filter(user=self.user).exists()
        except AdvancedChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def _save_message(self, room_id, sender, message_content):
        try:
            room = AdvancedChatRoom.objects.get(id=room_id)
            chat_message = AdvancedChatMessage.objects.create(
                chatroom=room,
                sender=sender,
                message_content=message_content,
                message_type='text'
            )
            return {
                'id': chat_message.id,
                'sender': sender.get_full_name() or sender.username,
                'sender_id': sender.id,
                'content': chat_message.message_content,
                'sent_at': chat_message.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        except Exception as e:
            print(f"Error saving message: {e}")
            return None

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            sender_id = data.get('sender_id')
            
            if not message or not sender_id:
                return

            # Get user
            user = await self._get_user(sender_id)
            if not user:
                return

            # Save message to database
            saved_message = await self._save_message(self.room_id, user, message)
            if not saved_message:
                return

            # Broadcast to all users in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': saved_message['content'],
                    'sender_id': saved_message['sender_id'],
                    'sender': saved_message['sender'],
                    'timestamp': saved_message['sent_at'],
                }
            )
        except Exception as e:
            print(f"Error in receive: {e}")

    @database_sync_to_async
    def _get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
        })) 