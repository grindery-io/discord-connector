import json
import base64
import requests
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .request_prefix import REQUEST_PREFIX


class SocketAdapter(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_tasks = set()
        self.connected = False

    async def connect(self):
        self.connected = True
        await self.accept()

    async def disconnect(self, close_code):
        self.connected = False
        print('-----socket disconnected-----')

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        request = json.loads(text_data)
        method = request.get("method", None)
        params = request.get("params", None)
        id = request.get("id", None)
        if method == 'ping':
            response = {
                'jsonrpc': '2.0',
                'result': {},
                'id': id
            }
            await self.send_json(response)
            return
        key = ''
        fields = ''
        session_id = ''
        channel = ''
        message = ''
        access_token = ''

        if params:
            if 'key' in params:
                key = params['key']
            if 'sessionId' in params:
                session_id = params['sessionId']
            if 'fields' in params:
                fields = params['fields']
                if 'channel' in fields:
                    channel = fields['channel']
                if 'message' in fields:
                    message = str(fields['message'])
            access_token = params['authentication']


        if method == 'runAction':
            try:
                header = {
                    'Authorization': 'Bearer ' + access_token,
                    'x-grindery-request-base64-authorization': base64.b64encode('Bot {{ secrets.bot_token }}'),
                    'Content-Type': 'application/json'
                }
                url = "https://discordapp.com/api/channels/{}/messages".format(channel)
                data = json.dumps({"content": message})
                res = requests.post(headers=header, url=url, data=data)
                run_action_response = {
                    'jsonrpc': '2.0',
                    'result': {
                        'key': key,
                        'sessionId': session_id,
                        'payload': {
                            'status': res.status_code,
                            'body': json.loads(res.content)
                        }
                    },
                    'id': id
                }

            except Exception as e:
                print("Error in WebSocket handler:", repr(e))
                run_action_response = {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 1,
                        'message': 'operation key is required'
                    },
                    'id': id
                }
            await self.send_json(run_action_response)
