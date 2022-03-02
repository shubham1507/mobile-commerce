import os

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'turtle_beans.settings')

    import django
    django.setup()
        
    from django.conf import settings
    from logging import getLogger
    import urllib
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    from apps.contacts.models import Reminder
    from fcm_django.models import FCMDevice
    from apps.notifications.models import Notifications, NotificationsImages

    start_reminder_day = (datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)
    end_reminder_day = start_reminder_day + relativedelta(days=1)

    logger = getLogger(__name__)

    reminders = Reminder.objects.filter(reminder_time__gte=start_reminder_day).filter(reminder_time__lt=end_reminder_day)

    for reminder in reminders:

        device = FCMDevice.objects.filter(user_id=reminder.buyer_id)
        device.send_message(title="Reminder", body="You have a reminder for today.")

        create_notification = Notifications.objects.create(
        user_id=reminder.buyer_id,
        Notification_image_id=NotificationsImages.objects.get(type='reminder').id,
        title='TurtleBeans',
        body='You have a reminder for today.',
        type='reminder')
