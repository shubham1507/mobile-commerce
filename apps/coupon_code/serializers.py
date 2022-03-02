from rest_framework import serializers
from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model  = Coupon
