from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class Cart(models.Model):
    buyer = models.ForeignKey('accounts.EmailUser')
    coffee = models.ForeignKey('coffee.Coffee')
    weight = models.ForeignKey('coffee.CoffeeWeight', blank=True, null=True)
    qty = models.ForeignKey('coffee.CoffeeQTY', blank=True, null=True)
    price = models.CharField(_('Coffee Price'),
                             max_length=50,
                             blank=True,
                             null=True)
    grind_type = models.ForeignKey('coffee.CoffeeGrindTypes',
                                   blank=True,
                                   null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.coffee)


class ShippingTypes(models.Model):
    SHIPPING_TYPE_CHOICES = (
        ('Free', 'Free'),
        ('Paid', 'Paid'),
    )

    shipping_type = models.CharField('Shippng Type',
                                     blank=True,
                                     null=True,
                                     max_length=32,
                                     choices=SHIPPING_TYPE_CHOICES)

    status = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.shipping_type)

    class Meta:
        verbose_name_plural = "Shipping Types"


class Shipping(models.Model):
    buyer = models.ForeignKey('accounts.EmailUser')
    phone_number = models.CharField(_('Phone Number'),
                                    max_length=15,
                                    blank=True,
                                    null=True)
    address_line_1 = models.TextField(blank=True, null=True)
    country = models.ForeignKey('accounts.Country', blank=True, null=True)
    state = models.ForeignKey('accounts.State', blank=True, null=True)
    city = models.ForeignKey('accounts.City',
                             blank=True,
                             null=True,
                             on_delete=models.SET_NULL)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    order_comments = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Shipping"


class OrderPlacedMappig(models.Model):
    user = models.ForeignKey('accounts.EmailUser', blank=True, null=True)
    price = models.FloatField(max_length=50, blank=False, null=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    coupon_discount_amount = models.FloatField(blank=True, null=True)
    cof_payment_successful = models.BooleanField(default=False)
    attachment = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.id)


class OrderPlaced(models.Model):
    buyer = models.ForeignKey('accounts.EmailUser',
                              related_name='buyer',
                              blank=True,
                              null=True)
    seller = models.ForeignKey('accounts.EmailUser',
                               related_name='seller',
                               blank=True,
                               null=True)
    coffee = models.ForeignKey('coffee.Coffee', blank=True, null=True)
    order_placed_mapping = models.ForeignKey('OrderPlacedMappig',
                                             blank=True,
                                             null=True)
    selected_grind = models.ForeignKey('coffee.CoffeeGrindTypes',
                                       blank=True,
                                       null=True)
    braintree_translation_id = models.TextField(blank=True, null=True)
    shipping = models.ForeignKey('Shipping', blank=True, null=True)
    weight = models.CharField(max_length=10, blank=True, null=True)
    qty = models.CharField(max_length=10, blank=True, null=True)
    price = models.FloatField(max_length=20, blank=True, null=True)
    shipping_charges = models.FloatField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Order Placed"


class RateReview(models.Model):
    buyer = models.ForeignKey('accounts.EmailUser', blank=True, null=True)
    coffee = models.ForeignKey('coffee.Coffee', blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Rate & Reviews"


class RateReviewComments(models.Model):
    user = models.ForeignKey('accounts.EmailUser',
                             models.CASCADE,
                             null=True,
                             blank=True)
    rate_review = models.ForeignKey('RateReview',
                                    models.CASCADE,
                                    blank=True,
                                    null=True)
    comment = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
