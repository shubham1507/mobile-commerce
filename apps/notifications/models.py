from django.db import models

# Create your models here.
class Notifications(models.Model):
    NOTIFICATIONS_TYPES_CHOICES = (
        ('first_order', 'First Order'),
        ('reminder', 'Reminder'),
        ('order_placed', 'Order Placed'),
        ('favourite', 'Favourite'),
        ('message', 'Message'),
        ('rate_review', 'Rate Review')
    )
    user = models.ForeignKey('accounts.EmailUser',
                             blank=True,
                             null=True)
    Notification_image = models.ForeignKey('NotificationsImages',
                                            blank=True,
                                            null=True)
    title = models.CharField(max_length=20,
                            blank=True,
                            null=True)
    body = models.TextField()
    type = models.CharField(max_length=50,
                            blank=True,
                            null=True,
                            choices=NOTIFICATIONS_TYPES_CHOICES)
    is_read = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True,
                                     blank=True,
                                     null=True)

    def __str__(self):
        return '{}'.format(self.title)


class NotificationsImages(models.Model):
    image = models.ImageField(upload_to='NotificationsImages/',
                              blank=True,
                              null=True)
    type = models.CharField(max_length=50,
                            blank=True,
                            null=True,
                            choices=Notifications.NOTIFICATIONS_TYPES_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True,
                                     blank=True,
                                     null=True)
