from django.contrib import admin

# Register your models here.
from .models import Message, TermsConditions, Reminder, ContactUs, ReportBug


class ReminderAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'reminder_time']
    list_filter = ['buyer', 'reminder_time']


class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'message']
    list_filter = ['user']


class ReportBugAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'message']
    list_filter = ['user']


admin.site.register(TermsConditions)
admin.site.register(Message)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(ReportBug, ReportBugAdmin)
