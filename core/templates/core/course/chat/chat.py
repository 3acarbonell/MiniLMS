from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

import json


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'chat_general'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_name = text_data_json['user_name']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_msg',
                'message': message,
                'user_name': user_name
            }
        )

    def chat_msg(self, event):
        message = event['message']
        user_name = event['user_name']

        self.send(text_data=json.dumps({
            'message': message,
            'user_name': user_name
        }))
