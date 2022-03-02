from rest_framework import serializers
from .models import Cart, Shipping, ShippingTypes, OrderPlaced, OrderPlacedMappig, RateReview, RateReviewComments
from apps.coffee.models import PriceWithSize
from apps.accounts.models import COFTOUSD


class CartSerializer(serializers.ModelSerializer):
    shipping_charge = serializers.SerializerMethodField()

    def get_shipping_charge(self, obj):

        # print("weight.id    " + str(obj.weight.id))
        # print(obj.coffee.id)
        shipping_charge = PriceWithSize.objects.filter(
            coffee_id=obj.coffee.id).filter(
                weight_id=obj.weight.id)[0].shipping_charge
        # print(shipping_charge)

        return shipping_charge

    class Meta:
        model = Cart
        fields = '__all__'


class ShippingTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingTypes
        fields = '__all__'


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = '__all__'


class OrderPlacedMappigSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPlacedMappig
        fields = '__all__'


class OrderPlacedSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='seller.company_name')
    shipping_charge = serializers.SerializerMethodField()

    def get_shipping_charge(self, obj):
        shipping_charge = PriceWithSize.objects.filter(
            coffee_id=obj.coffee.id).filter(
                weight_id=obj.weight.id)[0].shipping_charge
        return shipping_charge

    class Meta:
        model = OrderPlaced
        fields = '__all__'


class RateReviewSerializr(serializers.ModelSerializer):
    buyer_first_name = serializers.ReadOnlyField(source='buyer.first_name')
    buyer_last_name = serializers.ReadOnlyField(source='buyer.last_name')

    class Meta:
        model = RateReview
        fields = '__all__'


class RateReviewCommentsSerializer(serializers.ModelSerializer):
    user_first_name = serializers.ReadOnlyField(source='user.first_name')
    user_last_name = serializers.ReadOnlyField(source='user.last_name')

    class Meta:
        model = RateReviewComments
        fields = '__all__'
