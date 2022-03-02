from django.contrib import admin
from .models import Coupon

# Register your models here.

class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'valid_from', 'valid_to', 'percentage_discount', 'flat_discount',  'status']
    list_filter = ['status', 'valid_from', 'valid_to']
    search_fields = ['code']


admin.site.register(Coupon, CouponAdmin)
