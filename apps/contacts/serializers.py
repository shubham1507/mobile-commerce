from .models import Message, Reminder, TermsConditions, ContactUs, ReportBug
from rest_framework import serializers


class MessageSerializer(serializers.ModelSerializer):
    # sender_first_name = serializers.ReadOnlyField(source='sent_from.first_name')
    # sender_last_name = serializers.ReadOnlyField(source='sent_from.last_name')
    # receiver_first_name = serializers.ReadOnlyField(source='received_to.first_name')
    # receiver_last_name = serializers.ReadOnlyField(source='received_to.last_name')

    class Meta:
        model = Message
        fields = '__all__'


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'


class TermsConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsConditions
        fields = '__all__'


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'


class ReportBugSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportBug
        fields = '__all__'
