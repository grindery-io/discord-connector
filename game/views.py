import json
import requests
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ConnectorSerializer
from common.serializers import serialize_channel


class FetchChannelList(GenericAPIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_tasks = set()

    serializer_class = ConnectorSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        params = serializer.data.get('params')
        method = serializer.data.get('method')
        request_id = serializer.data.get('id')

        guild = ''

        key = params['key']
        if 'guild' in params['fieldData']:
            guild = params['fieldData']['guild']
        if 'channel' in params['fieldData']:
            channel = params['fieldData']['channel']
        access_token = params['credentials']['access_token']
        token_type = params['credentials']['token_type']
        expires_in = params['credentials']['expires_in']
        refresh_token = params['credentials']['refresh_token']
        scope = params['credentials']['scope']

        guilds = []
        channels = []

        if guild == '':
            try:
                header = {
                    'Authorization': token_type + ' ' + access_token,
                    'Content-Type': 'application/json'
                }
                url = "https://discordapp.com/api/users/@me/guilds"
                res = requests.get(headers=header, url=url)
                if res.status_code == 200:
                    for a_guild in json.loads(res.content):
                        guilds.append({
                            **serialize_channel(a_guild)
                        })
                return Response(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "inputFields": [
                                {
                                    "key": "guild",
                                    "label": "Discord account",
                                    "helpText": "",
                                    "type": "string",
                                    "required": True,
                                    "placeholder": "Choose...",
                                    "choices": guilds
                                }
                            ]
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception:
                return Response(
                    {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': 1,
                            'message': 'fetching server list is failed'
                        },
                        'id': id
                    },
                    status=status.HTTP_201_CREATED
                )
        else:
            try:
                header = {
                    'Authorization': token_type + ' ' + access_token,
                    'Content-Type': 'application/json'
                }
                url = "https://discordapp.com/api/guilds/{}/channels".format(guild)
                res = requests.get(headers=header, url=url)
                if res.status_code == 200:
                    for a_channel in json.loads(res.content):
                        if a_channel['type'] == 0:
                            channels.append({
                                **serialize_channel(a_channel)
                            })
                return Response(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "inputFields": [
                                {
                                    "key": "guild",
                                    "label": "Discord account",
                                    "helpText": "",
                                    "type": "string",
                                    "required": True,
                                    "placeholder": "Choose...",
                                    "choices": guilds
                                },
                                {
                                    "key": "channel",
                                    "label": "Channel",
                                    "helpText": "",
                                    "type": "string",
                                    "required": True,
                                    "placeholder": "Pick a channel...",
                                    "choices": channels
                                },
                            ]
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception:
                return Response(
                    {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': 1,
                            'message': 'operation is failed'
                        },
                        'id': id
                    },
                    status=status.HTTP_201_CREATED
                )
