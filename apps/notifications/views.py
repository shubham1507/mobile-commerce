from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import (ModelViewSet, ReadOnlyModelViewSet,
                                     GenericViewSet)
from .models import Notifications, NotificationsImages
from .serializers import NotificationsSerializer
from rest_framework.decorators import list_route, detail_route
from django.db.models import Count, functions, F, CharField
from django.db.models.functions import TruncDate
from django.core.paginator import Paginator


class NotificationsViewSet(ModelViewSet):
    serializer_class = NotificationsSerializer
    permission_classes = (AllowAny,)
    queryset = Notifications.objects.all()

    def get_queryset(self):
        q = self.queryset
        return q.all()


    @list_route(methods=['POST'])
    def user_notifications(self, request, *args, **kwargs):
        notifications = Notifications.objects.filter(user_id=request.user.id)
        read_notifications = notifications.update(is_read=True)
        times = notifications.annotate(timespan=TruncDate('timestamp')).values('timespan').order_by('-timespan').distinct()

        VALUES = [
            'id',
            'timestamp',
            'user_id',
            'title',
            'body',
            'type',
            'is_read',
            'Notification_image__image',
        ]

        notifications_dir = {}
        notifications_list = []
        for time in times:
            notification_obj = notifications.filter(
                timestamp__year = time['timespan'].year,
                timestamp__month = time['timespan'].month,
                timestamp__day = time['timespan'].day,
            ).order_by('-timestamp').values(*VALUES)
            notifications_dir['time'] = time['timespan']
            notifications_dir['value'] = notification_obj
            notifications_list.append(notifications_dir)
            notifications_dir = {}
        return Response(notifications_list)
