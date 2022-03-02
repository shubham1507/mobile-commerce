from django.shortcuts import render
from rest_framework import status, views, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import list_route, detail_route
from django.conf import settings
from fcm_django.models import FCMDevice
from apps.notifications.models import Notifications, NotificationsImages
from django.db.models import Count, functions
from django.db.models.functions import TruncDate
from django.db import connection
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.template.loader import get_template

from .models import Message, Reminder, TermsConditions, ContactUs, ReportBug
from .serializers import MessageSerializer, ReminderSerializer, TermsConditionsSerializer, ContactUsSerializer, ReportBugSerializer
from apps.accounts.models import EmailUser

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Message.objects.all()

    def get_queryset(self):
        q = self.queryset
        return q.all()


    def create(self, validated_data):
        serializer = MessageSerializer(
        data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        message=serializer.save()
        message.save()

        email_user = EmailUser.objects.get(id=self.request.data['sent_from'])
        full_name = str(email_user.first_name) + ' ' + str(email_user.last_name)
        device = FCMDevice.objects.filter(user_id=message.received_to).last()
        if device:
            device.send_message(title='TurtleBeans', body='You have a new message from ' + full_name + '.')
            create_notification = Notifications.objects.create(
            user_id=self.request.user.id,
            Notification_image_id=NotificationsImages.objects.get(type='message').id,
            title=str(message.subject),
            body=str(message.message),
            type='message')
        return Response(data={'result':True})


    @list_route(methods=['POST'])
    def messages(self, request, *args, **kwargs):
        if 'received_to' in request.data and 'user_id' in request.data:
            messages = Message.objects.filter(received_to__id=request.user.id)
        if 'sent_from' in request.data and 'user_id' in request.data:
            messages = Message.objects.filter(sent_from__id=request.user.id)

        messages.update(is_read=True)
        times = messages.annotate(timespan=TruncDate('timestamp')).values('timespan').order_by('-timespan').distinct()

        VALUES = [
            'id',
            'timestamp',
            'received_to',
            'sent_from',
            'subject',
            'message',
            'is_read',
            'received_to__first_name',
            'received_to__last_name',
            'sent_from__first_name',
            'sent_from__last_name'
        ]

        message_dir = {}
        message_list = []
        for time in times:
            message_obj = messages.filter(
                timestamp__year = time['timespan'].year,
                timestamp__month = time['timespan'].month,
                timestamp__day = time['timespan'].day,
            ).order_by('-timestamp').values(*VALUES)
            message_dir['time'] = time['timespan']
            message_dir['value'] = message_obj
            message_list.append(message_dir)
            message_dir = {}
        return Response(message_list)


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    queryset = Reminder.objects.all()

    def get_queryset(self):
        q = self.queryset
        if 'reminder_set' in self.request.query_params:
            return q.filter(buyer=self.request.user)
        return q.all()


class TermsConditionsViewSet(viewsets.ModelViewSet):
    serializer_class = TermsConditionsSerializer
    permission_classes = (AllowAny,)
    queryset = TermsConditions.objects.all()

    def get_queryset(self):
        q = self.queryset
        q = q.filter(status=True).order_by('-timestamp')
        return q.all()


class ContactUsViewSet(viewsets.ModelViewSet):
    serializer_class = ContactUsSerializer
    permission_classes = (IsAuthenticated,)
    queryset = ContactUs.objects.all()

    def create(self, validated_data):
        serializer = ContactUsSerializer(
        data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        contact_us=serializer.save()
        contact_us.save()

        plaintext = get_template('message/contact_us.txt')
        htmly     = get_template('message/contact_us.html')

        email_user = EmailUser.objects.get(id=self.request.data['user'])
        message_dir = {
            'template_title' : "Title",
            'user' : email_user.first_name + ' ' + email_user.last_name,
            'email' : email_user.email,
            'title' : self.request.data['subject'],
            'description' : self.request.data['message']
        }

        text_content = plaintext.render(message_dir)
        html_content = htmly.render(message_dir)

        subject = 'New request from ' + email_user.first_name + ' ' + email_user.last_name
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [settings.ADMINS])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return Response(data={'result':True})


class ReportBugViewSet(viewsets.ModelViewSet):
    serializer_class = ReportBugSerializer
    permission_classes = (IsAuthenticated,)
    queryset = ReportBug.objects.all()

    def create(self, validated_data):
        serializer = ReportBugSerializer(
        data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        report_bug=serializer.save()
        report_bug.save()

        plaintext = get_template('message/contact_us.txt')
        htmly     = get_template('message/contact_us.html')

        email_user = EmailUser.objects.get(id=self.request.data['user'])
        message_dir = {
            'template_title' : "Title",
            'user' : email_user.first_name + ' ' + email_user.last_name,
            'email' : email_user.email,
            'title' : self.request.data['subject'],
            'description' : self.request.data['message']
        }

        text_content = plaintext.render(message_dir)
        html_content = htmly.render(message_dir)

        subject = 'New request for a bug from ' + email_user.first_name + ' ' + email_user.last_name
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [settings.ADMINS])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return Response(data={'result':True})
