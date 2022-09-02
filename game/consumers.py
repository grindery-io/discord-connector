import json
import requests
from channels.generic.websocket import AsyncJsonWebsocketConsumer


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
        key = ''
        fields = ''
        session_id = ''
        access_token = ''
        token_type = ''
        refresh_token = ''
        channel = ''
        message = ''

        if params:
            if 'key' in params:
                key = params['key']
            if 'sessionId' in params:
                session_id = params['sessionId']
            if 'credentials' in params:
                credentials = params['credentials']
                if 'access_token' in credentials:
                    access_token = credentials['access_token']
                if 'refresh_token' in credentials:
                    refresh_token = credentials['refresh_token']
                if 'token_type' in credentials:
                    token_type = credentials['token_type']
            if 'fields' in params:
                fields = params['fields']
                if 'channel' in fields:
                    channel = fields['channel']
                if 'message' in fields:
                    message = str(fields['message'])

        if method == 'ping':
            response = {
                'jsonrpc': '2.0',
                'result': {},
                'id': id
            }
            await self.send_json(response)

        if method == 'runAction':
            try:
                header = {
                    'Authorization': token_type + ' ' + access_token,
                    'Content-Type': 'application/json'
                }
                url = "https://discordapp.com/api/channels/{}/messages".format(channel)
                data = json.dumps({"content": message})
                res = requests.post(headers=header, url=url, data=data)
                run_action_response = {
                    'jsonrpc': '2.0',
                    'result': {
                        'payload': {
                            'status': res.status_code,
                            'body': json.loads(res.content)
                        }
                    },
                    'id': id
                }

            except Exception as e:
                run_action_response = {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 1,
                        'message': 'operation key is required'
                    },
                    'id': id
                }
            await self.send_json(run_action_response)
