from rest_framework import fields
from rest_framework.serializers import Serializer


class LikesSerializer(Serializer):
    user_id = fields.IntegerField(read_only=True)
    post_id = fields.IntegerField()