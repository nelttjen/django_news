from abc import ABC

from rest_framework import fields
from rest_framework.serializers import Serializer, ModelSerializer
from user_profile.models import ExtendedUser


class LikesSerializer(Serializer):
    user_id = fields.IntegerField(read_only=True)
    post_id = fields.IntegerField()


class PostSerializer(ModelSerializer):
    class Meta:
        model = ExtendedUser
        fields = '__all__'
