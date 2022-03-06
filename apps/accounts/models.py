from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import EmailUserManager
from .permissions import BaseUserPermission
from django.utils.translation import gettext as _
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.urls import reverse

from apps.contacts.models import TermsConditions
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
# Create your models here.
"""
For our custom user model, we should start by inheriting from
the AbstractBaseUser and PermissionsMixin classes
"""


class GroupCountry(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.name)


class Country(models.Model):
    name = models.CharField(_('Country Name'),
                            max_length=200,
                            blank=True,
                            null=True)
    group_country = models.ForeignKey('GroupCountry',
                                      on_delete=models.SET_NULL,
                                      blank=True,
                                      null=True)
    currency_symbol = models.CharField(max_length=20, blank=True, null=True)
    weight_format = models.CharField(max_length=20, blank=True, null=True)
    braintree_merchanr_id = models.CharField(max_length=50,
                                             blank=True,
                                             null=True)
    rate = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _('Country')

    def __str__(self):
        return '{}'.format(self.name)


class BuyerAvailableCountry(models.Model):
    country = models.ForeignKey('Country', null=True,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class State(models.Model):
    name = models.CharField(_('State Name'),
                            max_length=200,
                            blank=True,
                            null=True)
    st = models.CharField(max_length=50, blank=True, null=True)
    country = models.ForeignKey('Country',
                                blank=True,
                                null=True,
                                on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _('State')

    def __str__(self):
        return '{}'.format(self.name)


class City(models.Model):
    name = models.CharField(_('City Name'),
                            max_length=200,
                            blank=True,
                            null=True)
    state = models.ForeignKey('State',
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL)
    country = models.ForeignKey('Country',
                                blank=True,
                                null=True,
                                on_delete=models.SET_NULL)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _('City')

    def __str__(self):
        return '{}'.format(self.name)


class EmailUser(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    company_name = models.CharField(_('Company Name'),
                                    max_length=300,
                                    blank=True)
    ABN = models.CharField(_('ABN'), max_length=200, blank=True)
    is_seller = models.BooleanField(_('is seller'), default=False)
    is_buyer = models.BooleanField(_('is buyer'), default=False)
    phone_number = models.CharField(_('Phone Number'),
                                    max_length=15,
                                    blank=True,
                                    null=True)
    birth_date = models.DateField(_("Date"), blank=True, null=True)
    country = models.ForeignKey('Country',
                                related_name='country',
                                blank=True,on_delete=models.CASCADE,
                                null=True)
    state = models.ForeignKey('State', blank=True, on_delete=models.CASCADE,null=True)
    city = models.ForeignKey('City',
                             blank=True,
                             null=True,
                             on_delete=models.SET_NULL)
    company_country = models.ForeignKey('Country',
                                        related_name='company_country',on_delete=models.CASCADE,
                                        blank=True,
                                        null=True)
    profile_description = models.TextField(blank=True, null=True)
    is_notification_sound = models.BooleanField(default=True)
    is_notification_vibrate = models.BooleanField(default=True)
    image = models.ImageField(upload_to='UserImages/', blank=True, null=True)
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    address_line_1 = models.TextField(blank=True, null=True)
    address_line_2 = models.TextField(blank=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    validated_at = models.DateTimeField(null=True, blank=True)
    validation_key = models.UUIDField(default=uuid.uuid4,
                                      null=True,
                                      blank=True)
    is_terms_conditions_accepted = models.BooleanField(default=False)
    terms_conditions = models.ForeignKey('contacts.TermsConditions',
                                         models.PROTECT,
                                         blank=True,
                                         null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_seller_approved = models.BooleanField(default=False)
    braintree_customer_id = models.TextField(blank=True, null=True)
    is_social = models.BooleanField(default=False)

    #Company Details
    company_logo = ProcessedImageField(upload_to='CompanyLogo/',
                                       processors=[ResizeToFill(250, 250)],
                                       format='JPEG',
                                       options={'quality': 60},
                                       blank=True,
                                       null=True)
    background_image = ProcessedImageField(upload_to='BackgroundImages/',
                                           processors=[ResizeToFill(550, 550)],
                                           format='JPEG',
                                           options={'quality': 60},
                                           blank=True,
                                           null=True)

    # Account Validation
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    validated_at = models.DateTimeField(null=True, blank=True)
    validation_key = models.UUIDField(default=uuid.uuid4,
                                      null=True,
                                      blank=True)

    objects = EmailUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []



    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

   
    def _send_html_mail(self, subject, template_html, template_text,
                        **context):
        """
        Renders templates to context, and uses EmailMultiAlternatives to
        send email.
        """
        if not template_html:
            raise ValueError('No HTML template provided for email.')
        if not template_text:
            raise ValueError('No text template provided for email.')
        default_context = {"settings": settings, "user": self}
        default_context.update(context)
        from_email = settings.DEFAULT_FROM_EMAIL
        body_text = render_to_string(template_text, default_context)
        body_html = render_to_string(template_html, default_context)

        msg = EmailMultiAlternatives(subject=subject,
                                     body=body_text,
                                     from_email=from_email,
                                     to=[self.email])
        msg.attach_alternative(body_html, 'text/html')
        msg.send()

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    # Set the user as active
    def validate(self) -> None:
        """
        Marks a user as validated and sends a confirmation email, clearing the
        validation_key so the validation link only works once.
        """
       
        self.validation_key = uuid.uuid4()
        self.validated_at = datetime.now()
        self.save()
        self._send_html_mail('Your account has been validated',
                             'email/user_validated.html',
                             'email/user_validated.txt')

    def send_validation_email(self):
        """
        Send email with a unique link using validation_key to validate account.
        """
        if self.is_social == False:
            self.validation_key = uuid.uuid4()
            self.save()
            self._send_html_mail(
                'Please validate your email address',
                'email/user_validation.html',
                'email/user_validation.txt',
                url='http://' + settings.SITE_DOMAIN +
                reverse('user-validation',
                        kwargs={"validation_key": self.validation_key}))

    def send_reset_password_email(self, request):
        """
        Send email with unique link to reset password. Create a new
        validation_key, which will be cleared once password is reset.
        """
        self.validation_key = uuid.uuid4()
        self.save()
        self._send_html_mail(
            'Password Reset Request',
            'email/user_reset_password.html',
            'email/user_reset_password.txt',
            url='http://' + settings.SITE_DOMAIN +
            reverse('reset-request',
                    kwargs={"validation_key": self.validation_key}))

    def send_reset_password_success_email(self):
        """
        Send email notifying users that their password was successfully reset.
        Validation key is cleared so the reset password link only works once.
        """
        self.validation_key = None
        self.save()
        self._send_html_mail('Password successfully changed',
                             'email/user_reset_password_success.html',
                             'email/user_reset_password_success.txt')


class COFTOUSD(models.Model):
    coin = models.IntegerField(default=1)
    coin_name = models.CharField(max_length=10, blank=True, null=True)
    usd = models.FloatField(blank=True, null=True)
    destination_address = models.CharField(max_length=50,
                                           blank=True,
                                           null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _('COF TO USD')


class AppVersion(models.Model):
    version = models.CharField(max_length=10, blank=True, null=True)
    status = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)


from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def validate_new_user(sender, instance, created, **kwargs):
    """Send a validation email when a new user is created."""
    if created and not instance.validated_at:
        instance.send_validation_email()
