from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

import json


class BoardConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'board_general'

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
        data = json.loads(text_data)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'draw_board',
                'x1': data['x1'],
                'y1': data['y1'],
                'x2': data['x2'],
                'y2': data['y2'],
                'color': data['color']
            }
        )

    def draw_board(self, event):
        self.send(text_data=json.dumps({
            'type': 'draw',
            'x1': event['x1'],
            'y1': event['y1'],
            'x2': event['x2'],
            'y2': event['y2'],
            'color': event['color']
        }))
