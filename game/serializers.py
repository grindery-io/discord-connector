from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class FieldDataSerializer(serializers.Serializer):
    guild = serializers.CharField(required=False)
    channel = serializers.CharField(required=False)

    class Meta:
        fields = ("guild", "channel")

    def validate(self, attrs):
        return attrs


class CredentialsSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True, allow_blank=True)
    token_type = serializers.CharField(required=False, allow_blank=True)
    expires_in = serializers.CharField(required=False, allow_blank=True)
    refresh_token = serializers.CharField(required=True, allow_blank=True)
    scope = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        fields = ("access_token", "token_type", "expires_in", "refresh_token", "scope")

    def validate(self, attrs):
        return attrs


class ParamSerializer(serializers.Serializer):
    key = serializers.CharField(required=False)
    fieldData = FieldDataSerializer()
    credentials = CredentialsSerializer()

    class Meta:
        fields = ("key", "credentials")

    def validate(self, attrs):
        return attrs


class ConnectorSerializer(serializers.Serializer):
    method = serializers.CharField()
    id = serializers.CharField()
    params = ParamSerializer()

    default_error_messages = {
        'invalid_type': _('type is invalid.'),
    }

    class Meta:
        fields = ("params", "method", "id")

    def validate(self, attrs):
        return attrs
