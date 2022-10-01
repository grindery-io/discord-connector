import json
import os
import requests
import base64
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ConnectorSerializer
from common.serializers import serialize_channel

from .request_prefix import REQUEST_PREFIX


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
        access_token = params['authentication']
        token_type = 'Bearer'

        guilds = []
        channels = []

        if guild == '':
            try:
                list_my = []
                unique_items = []

                header_my = {
                    'Authorization': token_type + ' ' + access_token,
                }
                url = REQUEST_PREFIX + "discordapp.com/api/users/@me/guilds"
                res_my = requests.get(headers=header_my, url=url)
                if res_my.status_code == 200:
                    for a_guild in json.loads(res_my.content):
                        # if a_guild['owner']:
                        list_my.append({
                            **serialize_channel(a_guild)
                        })

                header_bot = {
                    'Authorization': token_type + ' ' + access_token,
                    'x-grindery-request-base64-authorization': base64.b64encode(b'Bot {{ secrets.bot_token }}')
                }
                url = REQUEST_PREFIX + "discordapp.com/api/users/@me/guilds"
                res_bot = requests.get(headers=header_bot, url=url)
                if res_bot.status_code == 200:
                    for a_bot_guild in json.loads(res_bot.content):
                        list_my.append({
                            **serialize_channel(a_bot_guild)
                        })

                for item in list_my:
                    if item not in unique_items:
                        unique_items.append(item)
                    else:
                        guilds.append(item)

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
            except Exception as e:
                print("Error in HTTP handler:", repr(e))
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
                list_my = []
                unique_items = []

                header_my = {
                    'Authorization': token_type + ' ' + access_token
                }
                url = REQUEST_PREFIX + "discordapp.com/api/users/@me/guilds"
                res_my = requests.get(headers=header_my, url=url)
                if res_my.status_code == 200:
                    for a_guild in json.loads(res_my.content):
                        # if a_guild['owner']:
                        list_my.append({
                            **serialize_channel(a_guild)
                        })

                header_bot = {
                    'Authorization': token_type + ' ' + access_token,
                    'x-grindery-request-base64-authorization': base64.b64encode(b'Bot {{ secrets.bot_token }}')
                }
                url = REQUEST_PREFIX + "discordapp.com/api/users/@me/guilds"
                res_bot = requests.get(headers=header_bot, url=url)
                if res_bot.status_code == 200:
                    for a_bot_guild in json.loads(res_bot.content):
                        list_my.append({
                            **serialize_channel(a_bot_guild)
                        })

                for item in list_my:
                    if item not in unique_items:
                        unique_items.append(item)
                    else:
                        guilds.append(item)

                header = {
                    'Authorization': token_type + ' ' + access_token,
                    'x-grindery-request-base64-authorization': base64.b64encode(b'Bot {{ secrets.bot_token }}')
                }
                url = REQUEST_PREFIX + "discordapp.com/api/guilds/{}/channels".format(guild)
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
                                {
                                    "key": "message",
                                    "label": "Message Text",
                                    "helpText": "",
                                    "type": "string",
                                    "required": True,
                                    "placeholder": "Enter text"
                                }
                            ]
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                print("Error in HTTP handler:", repr(e))
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
