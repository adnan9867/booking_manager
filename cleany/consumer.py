import datetime
import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from booking.models import CustomerSupportChat, CustomerSupportCollection, DispatchedAppointment
from booking.utils import push_notifications
from user_module.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.booking_id = None
        self.booking_group_name = None
        self.sender = None
        self.chat_messages = []

    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.booking_group_name = 'chat_%s' % self.booking_id
        self.sender = self.scope['user']
        await self.chat_with_gpt()
        # Join booking group
        await self.channel_layer.group_add(
            self.booking_group_name,
            self.channel_name
        )
        messages = await self.get_chat_messages()
        for message in messages:
            self.chat_messages.append({
                'message': message['message'],
                "user": message['user__id'],
                "role": message['user__user_in_profile__role'],
                "created_at": str(message['created_at'].strftime("%Y-%m-%d %H:%M:%S")),
            })

        await self.accept()
        if self.chat_messages:
            for message in self.chat_messages:
                await self.send(text_data=json.dumps(message))

    async def disconnect(self, close_code):
        # Leave booking group
        await self.channel_layer.group_discard(
            self.booking_group_name,
            self.channel_name
        )

    # Receive message from WebSocket

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save chat message to database
        await self.save_chat_message(message)

        # Send message to booking group
        await self.channel_layer.group_send(
            self.booking_group_name,
            {
                'type': 'chat_message',
                'sender': self.sender.id,
                'message': message
            }
        )
        await self.send_notification_to_users(message)
        self.chat_messages.append({
            'sender': self.sender.id,
            'message': message,
            "role": self.sender.user_in_profile.role
        })

    async def chat_message(self, event):
        sender = event['sender']
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'user': sender,
            'message': message,
            "role": self.sender.user_in_profile.role,
            "created_at": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }))

    @sync_to_async
    def save_chat_message(self, message):
        from booking.models import Booking, CustomerSupportCollection, CustomerSupportChat
        booking = Booking.objects.get(id=self.booking_id)
        collection = CustomerSupportCollection.objects.get_or_create(
            booking=booking,
        )
        user = User.objects.filter(id=self.sender.id).first()
        chat_message = CustomerSupportChat.objects.create(
            collection=collection[0],
            user=user,
            message=message
        )
        return chat_message

    @database_sync_to_async
    def get_chat_messages(self):
        collection = CustomerSupportCollection.objects.filter(booking__id=self.booking_id).first()
        return list(CustomerSupportChat.objects.select_related("user").filter(collection=collection
                                                                              ).order_by('created_at'
                                                                                         ).values("message",
                                                                                                  "user__id",
                                                                                                  "user__user_in_profile__role",
                                                                                                  "created_at"
                                                                                                  )
                    )

    @database_sync_to_async
    def send_notification_to_users(self, event):
        try:
            message_title = "New message"
            if self.sender.user_in_profile.role == 'Customer':
                dispatch = DispatchedAppointment.objects.filter(booking__id=self.booking_id).first()
                if not dispatch:
                    return
                data = {"booking_id": self.booking_id}
                push_notifications(dispatch.service_provider, message_title, event, data=data)
            else:
                from booking.models import Booking
                booking = Booking.objects.get(id=self.booking_id)
                data = {"booking_id": self.booking_id}
                push_notifications(booking.bod.user, message_title, event, data)
        except Exception as e:  # pragma: no cover
            pass
