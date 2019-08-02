from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


class AnnotatorConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        if text_data == '"heartbeat"':
            # TODO: Put user presence code here
            print(text_data)
        else:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            self.send(text_data=json.dumps({'message': message}))
