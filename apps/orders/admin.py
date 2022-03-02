from django.contrib import admin

# Register your models here.
from .models import (Cart, ShippingTypes, Shipping, OrderPlaced,
                     OrderPlacedMappig, RateReview)


class CartAdmin(admin.ModelAdmin):
    list_display = ['coffee', 'buyer', 'weight', 'qty', 'price']
    list_filter = ['coffee', 'buyer']

class OrderPlacedAdmin(admin.ModelAdmin):

    list_display = ['buyer', 'seller', 'coffee', 'shipping', 'weight', 'qty', 'price']
    list_filter = ['buyer', 'seller', 'coffee']


class RateReviewAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'coffee', 'rating', 'title', 'status']
    list_filter = ['buyer', 'coffee', 'rating']
    search_fields = ('title', 'description')


class ShippingAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'phone_number', 'country', 'state', 'city']
    list_filter = ['buyer', 'postal_code', 'country']
    search_fields = ('buyer', 'address_line_1', 'postal_code', 'country', 'state', 'city')


admin.site.register(Cart, CartAdmin)
admin.site.register(Shipping, ShippingAdmin)
admin.site.register(OrderPlaced, OrderPlacedAdmin)
admin.site.register(RateReview, RateReviewAdmin)
admin.site.register(ShippingTypes)
admin.site.register(OrderPlacedMappig)
