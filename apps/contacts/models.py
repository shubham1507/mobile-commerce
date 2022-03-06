from django.db import models

# Create your models here.
class Message(models.Model):
    sent_from = models.ForeignKey('accounts.EmailUser',
                                  related_name='sent_from',
                                  blank=True,on_delete=models.CASCADE,
                                  null=True)
    received_to = models.ForeignKey('accounts.EmailUser',
                                    related_name='received_to',
                                    blank=True,on_delete=models.CASCADE,
                                    null=True)
    subject = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)



class Reminder(models.Model):
    buyer = models.ForeignKey('accounts.EmailUser',
                              blank=True,on_delete=models.CASCADE,
                              null=True)
    reminder_message = models.TextField(blank=True, null=True)
    reminder_time = models.DateField    (blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
       verbose_name_plural = "Reminder"


class TermsConditions(models.Model):
    terms_conditions = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
       verbose_name_plural = "Terms & Conditions"


class ContactUs(models.Model):
    user = models.ForeignKey('accounts.EmailUser',
                             blank=True,on_delete=models.CASCADE,
                             null=True)
    subject = models.CharField(max_length=300,
                            blank=True,
                            null=True)
    message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
       verbose_name_plural = "Contact Us"


class ReportBug(models.Model):
    user = models.ForeignKey('accounts.EmailUser',
                             blank=True,on_delete=models.CASCADE,
                             null=True)
    subject = models.CharField(max_length=300,
                            blank=True,
                            null=True)
    message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
