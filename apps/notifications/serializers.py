from django.conf import settings
from rest_framework import serializers
from rest_framework.response import Response
from .models import Notifications

class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'
