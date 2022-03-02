from django.conf import settings
from rest_framework import serializers
from rest_framework.response import Response
from apps.coffee.models import (CoffeeImages, PriceWithSize, Coffee,
                                CoffeeWeight, CoffeeQTY, CoffeeGrindTypes,
                                CoffeeSelectedGrindTypes, CoffeeLogos,
                                Favourite)
from apps.orders.models import RateReview, RateReviewComments, Cart
from apps.accounts.models import EmailUser, Country, COFTOUSD
from django.db.models import Avg, F
from urllib.request import urlopen
from bs4 import BeautifulSoup
REVIEWS_VALUES = [
    'coffee_id', 'buyer__first_name', 'buyer__last_name', 'rating',
    'timestamp', 'title', 'status', 'id', 'description'
]


class CoffeeImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoffeeImages
        fields = '__all__'


class CoffeeSerializer(serializers.ModelSerializer):
    coffee_images = serializers.SerializerMethodField()
    company_name = serializers.ReadOnlyField(source='seller.company_name')
    coffee_logo = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    reviewersCount = serializers.SerializerMethodField()
    seller_first_name = serializers.ReadOnlyField(source='seller.first_name')
    seller_last_name = serializers.ReadOnlyField(source='seller.last_name')
    is_favourite = serializers.SerializerMethodField()
    is_added_into_cart = serializers.SerializerMethodField()
    updated_weight = serializers.SerializerMethodField()
    updated_weight_country_id = serializers.SerializerMethodField()
    updated_qty = serializers.SerializerMethodField()
    updated_price = serializers.SerializerMethodField()
    grind_name = serializers.ReadOnlyField(source='grind.grind')
    weight_value = serializers.ReadOnlyField(source='weight.weight')
    qty_value = serializers.ReadOnlyField(source='qty.qty')
    seller_country_id = serializers.ReadOnlyField(source='seller.country_id')
    weight_format = serializers.SerializerMethodField()
    weight_country_id = serializers.SerializerMethodField()
    shipping_type_value = serializers.ReadOnlyField(
        source='shipping_type.shipping_type')
    top = serializers.ReadOnlyField(source='seller.state.top')
    left = serializers.ReadOnlyField(source='seller.state.left')
    special_weights = serializers.SerializerMethodField()
    special_grinds = serializers.SerializerMethodField()
    background_image = serializers.SerializerMethodField()
    coffee_currency = serializers.SerializerMethodField()
    selected_grind = serializers.SerializerMethodField()
    new_shipping_charge = serializers.SerializerMethodField()
    converted_prices = serializers.SerializerMethodField()
    cof_value = serializers.SerializerMethodField()
    qty_range = serializers.SerializerMethodField()

    def get_coffee_images(self, obj):
        list_images = []
        dir_coffee_images = {}
        request = self.context.get('request')
        coffee_images = CoffeeImages.objects.filter(coffee_id=obj.id)
        for coffee_image in coffee_images:
            dir_coffee_images['image'] = request.build_absolute_uri(
                coffee_image.image.url)
            dir_coffee_images['coffee_image_id'] = coffee_image.id
            dir_coffee_images['order'] = coffee_image.order
            list_images.append(dir_coffee_images)
            dir_coffee_images = {}
        return list_images

    def get_coffee_logo(self, obj):
        try:
            coffee_logo = EmailUser.objects.get(id=obj.seller.id).company_logo
            if coffee_logo:
                request = self.context.get('request')
                image_url = request.build_absolute_uri(coffee_logo.url)
                return image_url
        except Exception as e:
            return None

    def get_background_image(self, obj):
        try:
            background_image = EmailUser.objects.get(
                id=obj.seller.id).background_image
            if background_image:
                request = self.context.get('request')
                image_url = request.build_absolute_uri(background_image.url)
                return image_url
        except Exception as e:
            raise

    def get_rating(self, obj):
        ratings = RateReview.objects.filter(coffee_id=obj.id).exclude(
            rating__isnull=True).aggregate(Avg('rating'))
        return ratings['rating__avg']

    def get_reviews(self, obj):
        list_reviews = []
        dir_reviews = {}
        reviews = RateReview.objects.filter(coffee_id=obj.id).values(
            *REVIEWS_VALUES)

        VALUES = ['comment', 'timestamp', 'first_name', 'last_name', 'image']

        for review in reviews:
            dir_reviews['comments'] = RateReviewComments.objects.filter(
                rate_review=review['id']).annotate(
                    first_name=F('user__first_name'),
                    last_name=F('user__last_name'),
                    image=F('user__image')).values(
                        *VALUES).order_by('timestamp')
            try:
                review[
                    'image'] = 'https://turtlebeans-api.tersesoft.com/media/' + dir_reviews[
                        'comments'][0]['image']
            except:
                review['image'] = ''
            dir_reviews['review'] = review
            list_reviews.append(dir_reviews)
            dir_reviews = {}
        return list_reviews

    def get_reviewersCount(self, obj):
        reviewersCounts = RateReview.objects.filter(coffee_id=obj.id).exclude(
            title__isnull=True).count()
        return reviewersCounts

    def get_is_favourite(self, obj):
        if 'buyer_id' in self.context['request'].query_params:
            favourites = Favourite.objects.filter(
                buyer=self.context['request'].query_params['buyer_id']).filter(
                    coffee_id=obj.id).count()
            if favourites > 0:
                return True
            else:
                return False
        else:
            return False

    def get_is_added_into_cart(self, obj):
        if 'buyer_id' in self.context['request'].query_params:
            cart = Cart.objects.filter(
                buyer=self.context['request'].query_params['buyer_id']).filter(
                    coffee_id=obj.id).count()
            if cart > 0:
                return True
            else:
                return False
        else:
            return False

    def get_updated_weight(self, obj):
        if 'buyer_id' in self.context[
                'request'].query_params or 'cart_buyer_id' in self.context[
                    'request'].query_params:
            try:
                cart = Cart.objects.filter(buyer=self.context['request'].
                                           query_params['buyer_id']).filter(
                                               coffee_id=obj.id)
            except Exception as e:
                cart = Cart.objects.filter(
                    buyer=self.context['request'].query_params['cart_buyer_id']
                ).filter(coffee_id=obj.id)
            if len(cart) > 0:
                return cart[0].weight.weight
            else:
                return False

    def get_updated_weight_country_id(self, obj):
        if 'buyer_id' in self.context[
                'request'].query_params or 'cart_buyer_id' in self.context[
                    'request'].query_params:
            try:
                cart = Cart.objects.filter(buyer=self.context['request'].
                                           query_params['buyer_id']).filter(
                                               coffee_id=obj.id)
            except Exception as e:
                cart = Cart.objects.filter(
                    buyer=self.context['request'].query_params['cart_buyer_id']
                ).filter(coffee_id=obj.id)
            if len(cart) > 0:
                return cart[0].weight.country_id
            else:
                return False

    def get_updated_qty(self, obj):
        if 'buyer_id' in self.context[
                'request'].query_params or 'cart_buyer_id' in self.context[
                    'request'].query_params:
            try:
                cart = Cart.objects.filter(buyer=self.context['request'].
                                           query_params['buyer_id']).filter(
                                               coffee_id=obj.id)
            except Exception as e:
                cart = Cart.objects.filter(
                    buyer=self.context['request'].query_params['cart_buyer_id']
                ).filter(coffee_id=obj.id)
            if len(cart) > 0:
                return cart[0].qty.qty
            else:
                return False

    def get_updated_price(self, obj):
        if 'buyer_id' in self.context[
                'request'].query_params or 'cart_buyer_id' in self.context[
                    'request'].query_params:
            try:
                cart = Cart.objects.filter(buyer=self.context['request'].
                                           query_params['buyer_id']).filter(
                                               coffee_id=obj.id)
            except Exception as e:
                cart = Cart.objects.filter(
                    buyer=self.context['request'].query_params['cart_buyer_id']
                ).filter(coffee_id=obj.id)
            if len(cart) > 0:
                return float(cart[0].price)
            else:
                return False

    def get_weight_format(self, obj):
        if 'cart_buyer_id' in self.context['request'].query_params:
            buyer = EmailUser.objects.get(
                id=self.context['request'].query_params['cart_buyer_id'])
            return buyer.country.weight_format
        if 'buyer_id' in self.context['request'].query_params:
            buyer = EmailUser.objects.get(
                id=self.context['request'].query_params['buyer_id'])
            return buyer.country.weight_format
        if 'seller_id' in self.context['request'].query_params:
            buyer = EmailUser.objects.get(
                id=self.context['request'].query_params['seller_id'])
            return buyer.country.weight_format

    def get_weight_country_id(self, obj):
        try:
            return obj.weight.country_id
        except:
            return None

    def get_special_weights(self, obj):

        if 'buyer_id' in self.context['request'].query_params:

            VALUES = [
                'id',
                'coffee_id',
                'weight_id',
                'price',
                'weight_value',
                'weight_in_lb',
                'weight_format',
                'shipping_charge',
                #'inter_shipping_charge',
                'timestamp'
            ]
            buyer_obj = EmailUser.objects.get(
                id=self.context['request'].query_params['buyer_id'])

            print(buyer_obj)

            buyer_obj = buyer_obj.country_id
            seller_obj = obj.seller.country_id
            if buyer_obj == seller_obj:
                return (PriceWithSize.objects.filter(
                    coffee_id=obj.id).annotate(
                        weight_value=F('weight__weight'),
                        weight_format=F('weight__country__id'),
                        weight_in_lb=F('weight__weight_in_lb')).values(
                            *VALUES).order_by('weight__weight'))
            else:
                VALUES = [
                    'id',
                    'coffee_id',
                    'weight_id',
                    'price',
                    'weight_value',
                    'weight_in_lb',
                    'weight_format',
                    'inter_shipping_charge',
                    #'shipping_charge',
                    'timestamp'
                ]
                return PriceWithSize.objects.filter(coffee_id=obj.id).annotate(
                    weight_value=F('weight__weight'),
                    weight_format=F('weight__country__id'),
                    weight_in_lb=F('weight__weight_in_lb')).values(
                        *VALUES).order_by('weight__weight')
        else:
            VALUES = [
                'id', 'coffee_id', 'weight_id', 'price', 'weight_value',
                'weight_in_lb', 'weight_format', 'shipping_charge',
                'inter_shipping_charge', 'timestamp'
            ]
            return PriceWithSize.objects.filter(coffee_id=obj.id).annotate(
                weight_value=F('weight__weight'),
                weight_format=F('weight__country__id'),
                weight_in_lb=F('weight__weight_in_lb')).values(
                    *VALUES).order_by('weight__weight')

    def get_special_grinds(self, obj):
        VALUES = ['id', 'coffee_id', 'grind_id', 'grind_name', 'timestamp']
        return CoffeeSelectedGrindTypes.objects.filter(
            coffee_id=obj.id).annotate(grind_name=F('grind__grind')).values(
                *VALUES)

    def get_cof_value(self, obj):
        cof_to_usd_details_dir = {}
        cof_to_usd_obj = COFTOUSD.objects.get(coin_name='COF')
        cof_to_usd_details_dir['cof'] = cof_to_usd_obj.usd
        cof_to_usd_details_dir[
            'destination_address'] = cof_to_usd_obj.destination_address
        return cof_to_usd_details_dir

    def get_coffee_currency(self, obj):
        try:
            if 'cart_buyer_id' in self.context['request'].query_params:
                buyer_id = self.context['request'].query_params[
                    'cart_buyer_id']
            if 'buyer_id' in self.context['request'].query_params:
                buyer_id = self.context['request'].query_params['buyer_id']
            buyer = EmailUser.objects.get(id=buyer_id)
            currency = Country.objects.get(id=buyer.country_id).currency_symbol
        except Exception as e:
            currency = Country.objects.get(
                id=obj.seller.country_id).currency_symbol
        return currency

    def get_selected_grind(self, obj):
        try:
            if 'cart_buyer_id' in self.context['request'].query_params:
                weight_ids = CoffeeWeight.objects.values_list('id')
                qty_ids = CoffeeQTY.objects.values_list('id')
                selected_grind = Cart.objects.filter(coffee_id=obj.id).filter(
                    weight_id__in=weight_ids).filter(qty_id__in=qty_ids)
                if len(selected_grind) < 2:
                    selected_grind = selected_grind[0].grind_type.grind
                    return selected_grind
                else:
                    grind_list = []
                    selected_grind_ids = selected_grind.values_list(
                        'grind_type_id')
                    selected_grinds = CoffeeGrindTypes.objects.filter(
                        id__in=selected_grind_ids).values_list('grind')
                    for selected_grind in selected_grinds:
                        #    if: selected_grind[0]['final_shipping'] = 'domestic'
                        #else: selected_grind[0]['final_shipping'] = 'international'
                        #
                        grind_list.append(selected_grind[0])

                    return grind_list
        except Exception as e:
            return None

    def get_new_shipping_charge(self, obj):
        try:
            if 'cart_buyer_id' in self.context['request'].query_params:
                cart_coffee_weight_id = Cart.objects.filter(
                    coffee_id=obj.id).filter(
                        buyer_id=self.context['request'].
                        query_params['cart_buyer_id'])[0].weight_id
                new_shipping_charge = PriceWithSize.objects.filter(
                    coffee_id=obj.id).filter(
                        weight_id=cart_coffee_weight_id)[0].shipping_charge
                return new_shipping_charge
        except Exception as e:
            return None

    def get_converted_prices(self, obj):

        converted_price_dir = {}
        country_rate_obj = Country.objects.get(currency_symbol='USD')

        try:

            if 'buyer_id' in self.context['request'].query_params:

                buyer_obj = EmailUser.objects.get(
                    id=self.context['request'].query_params['buyer_id'])

                converted_price_dir['to_country_id'] = buyer_obj.country_id
            if 'cart_buyer_id' in self.context['request'].query_params:
                buyer_obj = EmailUser.objects.get(
                    id=self.context['request'].query_params['cart_buyer_id'])
                converted_price_dir['to_country_id'] = buyer_obj.country_id
            if 'seller_id' in self.context['request'].query_params:
                buyer_obj = EmailUser.objects.get(
                    id=self.context['request'].query_params['seller_id'])
                converted_price_dir['to_country_id'] = buyer_obj.country_id

            converted_price_dir['from_country_id'] = obj.seller.country_id

            converted_price_dir['converted_price'] = round(
                buyer_obj.country.rate / obj.seller.country.rate, 2)

            converted_price_dir['seller_id_usd'] = round(
                country_rate_obj.rate / obj.seller.country.rate, 2)

            converted_price_dir['buyer_id_usd'] = round(
                country_rate_obj.rate / buyer_obj.country.rate, 2)

            return converted_price_dir
        except Exception as e:
            raise

    def get_qty_range(self, obj):
        try:
            min_qty = obj.min_qty_pr_order
            max_qty = obj.max_qty_pr_order + 1
            return [qty_range for qty_range in range(min_qty, max_qty)]
        except Exception as e:
            return None

    class Meta:
        model = Coffee
        fields = '__all__'


class CoffeeWeightSerializer(serializers.ModelSerializer):
    weight_format = serializers.ReadOnlyField(source='country.weight_format')

    class Meta:
        model = CoffeeWeight
        fields = '__all__'


class PriceWithSizeSerializer(serializers.ModelSerializer):
    final_shipping = serializers.SerializerMethodField()

    def get_final_shipping(self, obj):
        if 'buyer_id' in self.context['request'].query_params:
            buyer_obj = EmailUser.objects.get(
                id=self.context['request'].query_params['buyer_id'])
            buyer_obj = buyer_obj.country_id
            seller_obj = obj.seller.country_id
            if buyer_obj == seller_obj:
                return obj.shipping_charge
            else:
                return obj.inter_shipping_charge
        else:
            pass

    class Meta:
        model = PriceWithSize
        fields = '__all__'


class CoffeeSelectedGrindTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoffeeSelectedGrindTypes
        fields = '__all__'


class CoffeeQTYSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoffeeQTY
        fields = '__all__'


class CoffeeGrindTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoffeeGrindTypes
        fields = '__all__'


class CoffeeAddUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coffee
        fields = '__all__'


class CoffeeLogosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoffeeLogos
        fields = '__all__'


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = '__all__'
