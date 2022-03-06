from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import EmailUser


class CoffeeImages(models.Model):
    image = ProcessedImageField(upload_to='CoffeeImages/',
                                processors=[ResizeToFill(250, 250)],
                                format='JPEG',
                                options={'quality': 60},
                                null=True)
    coffee = models.ForeignKey('Coffee', blank=True, null=True, on_delete=models.CASCADE)
    order = models.IntegerField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return '{}'.format(self.image)

    class Meta:
        verbose_name_plural = "Coffee Images"


class CoffeeWeight(models.Model):
    weight = models.FloatField(blank=True, null=True)
    weight_in_lb = models.FloatField(blank=True, null=True)
    country = models.ForeignKey('accounts.Country',  on_delete=models.CASCADE,blank=True, null=True)
    group = models.ForeignKey('accounts.GroupCountry',  on_delete=models.CASCADE,blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.weight)

    class Meta:
        verbose_name_plural = "Coffee Weight"


class CoffeeQTY(models.Model):
    qty = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.qty)

    class Meta:
        verbose_name_plural = 'Coffee QTY'


class CoffeeGrindTypes(models.Model):
    grind = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.grind)

    class Meta:
        verbose_name_plural = "Coffee Grind Types"


class PriceWithSize(models.Model):
    coffee = models.ForeignKey('Coffee',  on_delete=models.CASCADE,blank=True, null=True)
    weight = models.ForeignKey('CoffeeWeight', on_delete=models.CASCADE, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    shipping_charge = models.FloatField(blank=True, null=True)
    inter_shipping_charge = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class CoffeeSelectedGrindTypes(models.Model):
    coffee = models.ForeignKey('Coffee',  on_delete=models.CASCADE,blank=True, null=True)
    grind = models.ForeignKey('CoffeeGrindTypes', on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Coffee(models.Model):
    excerpt = models.TextField()
    description = models.TextField(_('Description'), blank=True, null=True)
    discount_price = models.FloatField(_('Discount Price'),
                                       blank=True,
                                       null=True)
    cover_image = models.ImageField(upload_to='CoverImages/',
                                    blank=True,
                                    null=True)
    name = models.CharField(_('Name'), max_length=300, blank=True, null=True)
    price = models.FloatField(_('Price'), blank=True, null=True)
    weight = models.ForeignKey('CoffeeWeight', blank=True, null=True, on_delete=models.CASCADE,)
    qty = models.ForeignKey('CoffeeQTY', blank=True, null=True, on_delete=models.CASCADE)
    grind = models.ForeignKey('CoffeeGrindTypes', blank=True, null=True, on_delete=models.CASCADE)
    coffee_from = models.CharField(_('Coffee From'),
                                   max_length=300,
                                   blank=True,
                                   null=True)
    variety = models.CharField(_('Variety'),
                               max_length=300,
                               blank=True,
                               null=True)
    aroma = models.CharField(_('Aroma'), max_length=300, blank=True, null=True)
    acidity = models.CharField(_('Acidity'),
                               max_length=300,
                               blank=True,
                               null=True)
    body = models.CharField(max_length=300, blank=True, null=True)
    seller = models.ForeignKey('accounts.EmailUser',  on_delete=models.CASCADE,blank=True, null=True)
    is_sale = models.BooleanField(default=False)
    is_sold_out = models.BooleanField(default=False)
    shipping_type = models.ForeignKey('orders.ShippingTypes', on_delete=models.CASCADE,
                                      blank=True,
                                      null=True)
    inter_shipping_charge = models.FloatField(blank=True, null=True)
    shipping_charge = models.FloatField(blank=True, null=True)
    status = models.BooleanField(default=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    min_qty_pr_order = models.IntegerField(blank=True, null=True)
    max_qty_pr_order = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name_plural = "Coffee"


class CoffeeLogos(models.Model):
    user = models.ForeignKey('accounts.EmailUser',
                             models.CASCADE,
                             blank=True,
                             null=True)
    coffee = models.OneToOneField('Coffee',
                               models.CASCADE,
                               unique=True,
                               blank=True,
                               null=True)
    company_logo = ProcessedImageField(upload_to='CompanyLogo/',
                                       processors=[ResizeToFill(250, 250)],
                                       format='JPEG',
                                       options={'quality': 60},
                                       null=True)

    class Meta:
        verbose_name_plural = _('Coffee Logos')


class Favourite(models.Model):
    buyer = models.ForeignKey('accounts.EmailUser',  on_delete=models.CASCADE,blank=True, null=True)
    coffee = models.ForeignKey('Coffee',  on_delete=models.CASCADE,blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
