from django.shortcuts import render
from django.db.models import F, Sum, Avg
from rest_framework import status, views, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import list_route, detail_route
from .models import Cart, ShippingTypes, Shipping, OrderPlaced, OrderPlacedMappig, RateReview, RateReviewComments
from .serializers import (CartSerializer, ShippingTypesSerializer, ShippingSerializer, OrderPlacedSerializer,
                          OrderPlacedMappigSerializer, RateReviewSerializr, RateReviewCommentsSerializer)
# from apps.coffee.models import Coffee, CoffeeWeight, CoffeeQTY, CoffeeImages
from apps.coffee.models import *
from apps.accounts.models import Country, COFTOUSD
from apps.notifications.models import Notifications, NotificationsImages
from fcm_django.models import FCMDevice
import datetime
from dateutil.relativedelta import relativedelta
# Create your views here.

REVIEWS_VALUES = ['coffee_id', 'buyer__first_name', 'buyer__last_name',
                  'rating', 'timestamp', 'title', 'status', 'id', 'description']

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Cart.objects.all()

    def get_queryset(self):
        q = self.queryset
        if 'buyer_id' in self.request.query_params:
            return q.filter(buyer_id=self.request.query_params['buyer_id']).filter(coffee__is_sold_out=False)
        return q.all()

    @list_route(methods=['POST'])
    def add_to_cart(self, request, *args, **kwargs):
        q = self.queryset
        coffee_QT = CoffeeQTY.objects.get(id=request.data['qty'])
        coffee_qty = Coffee.objects.get(id=request.data['coffee'])
        if coffee_QT.qty >= coffee_qty.min_qty_pr_order and coffee_QT.qty <= coffee_qty.max_qty_pr_order:
            cart_obj, created = Cart.objects.get_or_create(buyer_id=request.data['buyer'], coffee_id=request.data['coffee'], grind_type_id=request.data['grind_type'])
            if cart_obj:
                if coffee_QT.qty >= coffee_qty.min_qty_pr_order and coffee_QT.qty <= coffee_qty.max_qty_pr_order:
                    weight = CoffeeWeight.objects.get(weight=request.data['weight'], country_id=request.data['country_id'])
                    if cart_obj.weight_id == weight.id and cart_obj.qty_id == request.data['qty'] and cart_obj.price == request.data['price'] and cart_obj.grind_type_id == request.data['grind_type']:
                        return Response(data={'result':'false'})
                    else:
                        if coffee_QT.qty >= coffee_qty.min_qty_pr_order and coffee_QT.qty <= coffee_qty.max_qty_pr_order:
                            cart_obj.weight_id = weight.id
                            cart_obj.qty_id = request.data['qty']
                            cart_obj.price = request.data['price']
                            cart_obj.save()
                            return Response(data={'result':'success'})
                        else:
                            return Response(data={'result':'false', 'message':'Please choose quantity between ' + str(coffee_qty.min_qty_pr_order) + ' to ' + str(coffee_qty.max_qty_pr_order)})
                else:
                    return Response(data={'result':'false', 'message':'Please choose quantity between ' + str(coffee_qty.min_qty_pr_order) + ' to ' + str(coffee_qty.max_qty_pr_order)})
        else:
            return Response(data={'result':'false', 'message':'Please choose quantity between ' + str(coffee_qty.min_qty_pr_order) + ' to ' + str(coffee_qty.max_qty_pr_order)})

    @list_route(methods=['POST'])
    def remove_from_cart(self, request, *args, **kwargs):
        q = self.queryset
        remove_cart_products = q.filter(
                               buyer_id=request.data['buyer_id']).filter(
                               coffee_id=request.data['coffee_id'],
                               grind_type_id=request.data['grind_type_id']).delete()
        return JsonResponse({'result':'true'})


    @list_route(methods=['POST'])
    def update_cart(self, request, *args, **kwargs):
        q = self.queryset
        update_cart_details = q.filter(
                              buyer_id=request.data['buyer_id']).filter(
                              coffee_id=request.data['coffee_id']).filter(
                              grind_type_id=request.data['grind_type_id']).update(
                              qty=request.data['qty'], price=request.data['price'])
        return Response(data={'result':True})


    @list_route(methods=['GET'])
    def cart_orders(self, request):

        list_reviews = []
        dir_reviews = {}
        list_images = []
        dir_coffee_images = {}
        cart_details_dir = {}
        cart_details_list = []
        cart_buyer_id = request.query_params['cart_buyer_id']
        buyer_obj = EmailUser.objects.get(id=cart_buyer_id)
        cart_products = Cart.objects.filter(buyer_id=cart_buyer_id)
        country_rate_obj = Country.objects.get(currency_symbol='USD')

        for cart_product in cart_products:
            cart_details_dir['qty_id'] = cart_product.qty_id
            cart_details_dir['weight_id'] = cart_product.weight_id
            cart_details_dir['grind_type_id'] = cart_product.grind_type_id
            cart_details_dir['buyer_id_usd'] = round(country_rate_obj.rate/buyer_obj.country.rate, 2)

            coffee_details = Coffee.objects.filter(id=cart_product.coffee_id).values()
            cart_details_dir['coffee'] = coffee_details
            cart_details_dir['qty_range'] = [qty_range for qty_range in range((coffee_details[0])['min_qty_pr_order'], (coffee_details[0])['max_qty_pr_order'] + 1)]



            # request = self.context.get('request')
            coffee_images = CoffeeImages.objects.filter(coffee_id=cart_product.coffee_id)
            for coffee_image in coffee_images:
                dir_coffee_images['image'] = request.build_absolute_uri(coffee_image.image.url)
                dir_coffee_images['coffee_image_id'] = coffee_image.id
                dir_coffee_images['order'] = coffee_image.order
                list_images.append(dir_coffee_images)
                dir_coffee_images = {}
            cart_details_dir['coffee_images'] =  list_images


            cart_details_dir['company_name'] = cart_product.coffee.seller.company_name


            try:
                coffee_logo = EmailUser.objects.get(id=cart_product.coffee.seller.id).company_logo
                if coffee_logo:
                    request = self.context.get('request')
                    image_url = request.build_absolute_uri(coffee_logo.url)
                else:
                    image_url = None
            except Exception as e:
                image_url = None
            cart_details_dir['coffee_logo'] = image_url


            ratings = RateReview.objects.filter(coffee_id=cart_product.coffee_id).exclude(rating__isnull=True).aggregate(Avg('rating'))
            cart_details_dir['rating'] = ratings['rating__avg']



            reviews = RateReview.objects.filter(coffee_id=cart_product.coffee_id).values(*REVIEWS_VALUES)
            VALUES = [
                'comment',
                'timestamp',
                'first_name',
                'last_name'
            ]
            for review in reviews:
                dir_reviews['review'] = review
                dir_reviews['comments'] = RateReviewComments.objects.filter(rate_review=review['id']).annotate(
                first_name=F('user__first_name'),
                last_name=F('user__last_name')
                ).values(*VALUES).order_by('timestamp')
                list_reviews.append(dir_reviews)
                dir_reviews = {}
            cart_details_dir['reviews'] = list_reviews


            reviewersCounts = RateReview.objects.filter(coffee_id=cart_product.coffee_id).exclude(title__isnull=True).count()
            cart_details_dir['reviewersCount'] = reviewersCounts


            cart_details_dir['seller_first_name'] = cart_product.coffee.seller.first_name
            cart_details_dir['seller_last_name'] = cart_product.coffee.seller.last_name


            favourites = Favourite.objects.filter(buyer_id=cart_buyer_id).filter(coffee_id=cart_product.coffee_id).count()
            if favourites > 0:
                favourites = True
            else:
                favourites = False
            cart_details_dir['is_favourite'] = favourites



            cart = Cart.objects.filter(buyer_id=cart_buyer_id).filter(coffee_id=cart_product.coffee_id).count()
            if cart > 0:
                is_added_into_cart = True
            else:
                is_added_into_cart = False
            cart_details_dir['is_added_into_cart'] = is_added_into_cart

            cart_details_dir['updated_weight'] = cart_product.weight.weight

            cart_details_dir['updated_weight_in_lb'] = cart_product.weight.weight_in_lb

            cart_details_dir['updated_weight_country_id'] = cart_product.weight.country_id

            cart_details_dir['updated_qty'] = cart_product.qty.qty

            cart_details_dir['updated_price'] = cart_product.price

            try:
                grind_name = cart_product.grind_type.grind
            except Exception as e:
                grind_name = None
            cart_details_dir['grind_name'] = grind_name

            cart_details_dir['weight_value'] = cart_product.coffee.weight.weight

            # cart_details_dir['qty_value'] = cart_product.coffee.qty.qty

            cart_details_dir['seller_country_id'] = cart_product.coffee.seller.country_id

            cart_details_dir['weight_format'] = EmailUser.objects.get(id=cart_buyer_id).country.weight_format

            cart_details_dir['weight_country_id'] = cart_product.coffee.weight.country_id

            cart_details_dir['shipping_type_value'] = cart_product.coffee.shipping_type.shipping_type

            seller_country = cart_product.coffee.seller.country_id
            buyer_country = EmailUser.objects.get(id=cart_buyer_id).country_id
            if seller_country == buyer_country:
                VALUES = [
                    'id',
                    'coffee_id',
                    'weight_id',
                    'price',
                    'weight_value',
                    'weight_in_lb',
                    'weight_format',
                    'shipping_charge',
                    'timestamp'
                ]
                special_weights = PriceWithSize.objects.filter(coffee_id=cart_product.coffee_id).annotate(
                                  weight_value=F('weight__weight'),
                                  weight_format=F('weight__country__id'),
                                  weight_in_lb=F('weight__weight_in_lb')
                                  ).values(*VALUES).order_by('weight__weight')
                cart_details_dir['special_weights'] = special_weights
            else:
                VALUES = [
                    'id',
                    'coffee_id',
                    'weight_id',
                    'price',
                    'weight_value',
                    'weight_in_lb',
                    'weight_format',
                    #'shipping_charge',
                    'inter_shipping_charge',
                    'timestamp'
                ]
                special_weights = PriceWithSize.objects.filter(coffee_id=cart_product.coffee_id).annotate(
                                  weight_value=F('weight__weight'),
                                  weight_format=F('weight__country__id'),
                                  weight_in_lb=F('weight__weight_in_lb')
                                  ).values(*VALUES).order_by('weight__weight')
                cart_details_dir['special_weights'] = special_weights


            VALUES = [
                'id',
                'coffee_id',
                'grind_id',
                'grind_name',
                'timestamp'
            ]
            special_grinds = CoffeeSelectedGrindTypes.objects.filter(coffee_id=cart_product.coffee_id).annotate(
                             grind_name=F('grind__grind')
                             ).values(*VALUES)
            cart_details_dir['special_grinds'] = special_grinds

            try:
                background_image = EmailUser.objects.get(id=cart_product.coffee.seller_id).background_image
                if background_image:
                    image_url = request.build_absolute_uri(background_image.url)
                    background_image = image_url
                else:
                    background_image = None
            except Exception as e:
                background_image = None
            cart_details_dir['background_image'] = background_image


            buyer = EmailUser.objects.get(id=cart_buyer_id)
            currency = Country.objects.get(id=buyer.country_id).currency_symbol
            cart_details_dir['coffee_currency'] = currency

            try:
                new_shipping_charge = PriceWithSize.objects.filter(
                                   coffee_id=cart_product.coffee_id).filter(
                                   weight_id=cart_product.weight_id)[0].shipping_charge
                cart_details_dir['new_shipping_charge'] = new_shipping_charge
            except:
                new_shipping_charge = None
                cart_details_dir['new_shipping_charge'] = new_shipping_charge

            coffee_details = coffee_details[0]
            cart_details_dir['id'] = coffee_details['id']
            cart_details_dir['coffee_id'] = coffee_details['id']
            cart_details_dir['excerpt'] = coffee_details['excerpt']
            cart_details_dir['description'] = coffee_details['description']
            cart_details_dir['discount_price'] = coffee_details['discount_price']
            cart_details_dir['cover_image'] = coffee_details['cover_image']
            cart_details_dir['name'] = coffee_details['name']
            cart_details_dir['price'] = coffee_details['price']
            cart_details_dir['coffee_from'] = coffee_details['coffee_from']
            cart_details_dir['variety'] = coffee_details['variety']
            cart_details_dir['aroma'] = coffee_details['aroma']
            cart_details_dir['acidity'] = coffee_details['acidity']
            cart_details_dir['body'] = coffee_details['body']
            cart_details_dir['seller'] = coffee_details['seller_id']
            cart_details_dir['seller_id'] = coffee_details['seller_id']
            cart_details_dir['is_sale'] = coffee_details['is_sale']
            cart_details_dir['is_sold_out'] = coffee_details['is_sold_out']
            cart_details_dir['shipping_type_id'] = coffee_details['shipping_type_id']
            cart_details_dir['shipping_charge'] = coffee_details['shipping_charge']
            cart_details_dir['status'] = coffee_details['status']
            cart_details_dir['latitude'] = coffee_details['latitude']
            cart_details_dir['longitude'] = coffee_details['longitude']

            converted_price_dir = {}
            buyer_obj = EmailUser.objects.get(id=cart_buyer_id)
            converted_price_dir['to_country_id'] = buyer_obj.country_id
            converted_price_dir['from_country_id'] = cart_product.coffee.seller.country_id
            converted_price_dir['converted_price'] = round(buyer_obj.country.rate/cart_product.coffee.seller.country.rate, 2)
            cart_details_dir['converted_prices'] = converted_price_dir

            cof_to_usd_details_dir = {}
            cof_to_usd_obj = COFTOUSD.objects.get(coin_name='COF')
            cof_to_usd_details_dir['cof'] = cof_to_usd_obj.usd
            cof_to_usd_details_dir['destination_address'] = cof_to_usd_obj.destination_address
            cart_details_dir['cof_value'] = cof_to_usd_details_dir


            cart_details_list.append(cart_details_dir)
            cart_details_dir = {}
            converted_price_dir = {}
            cof_to_usd_details_dir = {}
            list_reviews = []
            list_images = []
        return Response(cart_details_list)

class ShippingTypesViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingTypesSerializer
    permission_classes = (IsAuthenticated,)
    queryset = ShippingTypes.objects.all()


class ShippingViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Shipping.objects.all()


class OrderPlacedMappigViewSet(viewsets.ModelViewSet):
    serializer_class = OrderPlacedMappigSerializer
    permission_classes = (IsAuthenticated,)
    queryset = OrderPlacedMappig.objects.all()


class OrderPlacedViewSet(viewsets.ModelViewSet):
    serializer_class = OrderPlacedSerializer
    permission_classes = (IsAuthenticated,)
    queryset = OrderPlaced.objects.all()

    def get_queryset(self):
        q = self.queryset
        if 'is_seller' in self.request.query_params:
            return q.filter(seller_id=self.request.user.id).order_by('-timestamp')
        if 'is_buyer' in self.request.query_params:
            return q.filter(buyer_id=self.request.user.id).order_by('-timestamp')
        return q.all()

    @list_route(methods=['POST'])
    def my_orders(self, request, *args, **kwargs):
        my_orders_dict = {}
        my_orders_list = []

        if 'all_orders' not in request.data:
            selected_months = (datetime.datetime.today() - relativedelta(months=request.data['months']))

        if 'is_seller' in request.data:
            selected_months = (datetime.datetime.today() - relativedelta(months=request.data['months']))

            if 'all_orders' in request.data:
                order_placed_mapping_ids = OrderPlaced.objects.filter(seller_id=request.user.id).values_list(
                'order_placed_mapping_id').distinct().order_by('-order_placed_mapping_id')
            else:
                order_placed_mapping_ids = OrderPlaced.objects.filter(timestamp__lte=datetime.datetime.today()).filter(
                timestamp__gte=selected_months).filter(seller_id=request.user.id).values_list(
                'order_placed_mapping_id').distinct().order_by('-order_placed_mapping_id')

            for order_placed_mapping_id in order_placed_mapping_ids:
                orders = OrderPlaced.objects.filter(order_placed_mapping_id=order_placed_mapping_id)

                orders = orders.annotate(
                    seller_first_name=F('seller__first_name'),
                    seller_last_name=F('seller__last_name'),
                    company_name=F('seller__company_name'),
                    coffee_name=F('coffee__name'),
                    coffee_currency=F('coffee__seller__country__currency_symbol'),
                    attachment=F('order_placed_mapping__attachment'),
                    grind=F('selected_grind__grind'),
                    cof_payment_successful=F('order_placed_mapping__cof_payment_successful')).order_by('-timestamp').values()


                sub_total = orders.aggregate(Sum('price'))
                my_orders_dict['order_no'] = order_placed_mapping_id[0]
                my_orders_dict['coffee'] = orders
                my_orders_dict['sub_total'] = OrderPlacedMappig.objects.get(id=order_placed_mapping_id[0]).price
                my_orders_dict['orderDateTime'] = OrderPlacedMappig.objects.get(id=order_placed_mapping_id[0]).timestamp
                my_orders_list.append(my_orders_dict)
                my_orders_dict = {}
            return Response(my_orders_list)

        ordersMapping = OrderPlacedMappig.objects.filter(user_id=request.user.id).order_by('-timestamp').values()
        COFTOUSD_obj = COFTOUSD.objects.get(coin_name='COF')

        for orderMapping in ordersMapping:
            if 'all_orders' in request.data:
                orders = OrderPlaced.objects.filter(order_placed_mapping_id=orderMapping['id']).filter(
                buyer_id=request.user.id)
            else:
                orders = OrderPlaced.objects.filter(timestamp__lte=datetime.datetime.today()).filter(
                timestamp__gte=selected_months).filter(order_placed_mapping_id=orderMapping['id']).filter(
                buyer_id=request.user.id)

            orders = orders.annotate(
            seller_first_name=F('seller__first_name'),
            seller_last_name=F('seller__last_name'),
            company_name=F('seller__company_name'),
            coffee_name=F('coffee__name'),
            grind=F('selected_grind__grind'),
            coffee_currency=F('coffee__seller__country__currency_symbol')).order_by('-timestamp').values()

            sub_total = orders.aggregate(Sum('price'))
            my_orders_dict['order_no'] = orderMapping
            my_orders_dict['coffee'] = orders
            my_orders_dict['sub_total'] = sub_total
            my_orders_dict['orderDateTime'] = orderMapping['timestamp']
            my_orders_dict['destination_address'] = COFTOUSD_obj.destination_address
            my_orders_list.append(my_orders_dict)
            my_orders_dict = {}
        return Response(my_orders_list)

class RateReviewViewSet(viewsets.ModelViewSet):
    serializer_class = RateReviewSerializr
    permission_classes = (IsAuthenticated,)
    queryset = RateReview.objects.all()

    def get_queryset(self):
        q = self.queryset.filter(status=True)
        return q.all()

    def create(self, validated_data):
        serializer = RateReviewSerializr(
        data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        rate_review=serializer.save()
        rate_review.save()

        device = FCMDevice.objects.filter(user_id=rate_review.coffee.seller_id).last()
        if device:
            device.send_message(title='TurtleBeans', body='You just got a rating on the ' + str(rate_review.coffee.name) + ' product.')
            create_notification = Notifications.objects.create(
            user_id=self.request.user.id,
            Notification_image_id=NotificationsImages.objects.get(type='rate_review').id,
            title='TurtleBeans',
            body='You just got a rating on the ' + str(rate_review.coffee.name) + ' product.',
            type='rate_review')
        return Response(data={'result':True})


class RateReviewCommentsViewSet(viewsets.ModelViewSet):
    serializer_class = RateReviewCommentsSerializer
    permission_classes = (IsAuthenticated,)
    queryset = RateReviewComments.objects.all()

    def get_queryset(self):
        q = self.queryset
        return q.all()

    def create(self, validated_data):
        serializer = RateReviewCommentsSerializer(
        data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        rateReview_comment=serializer.save()
        rateReview_comment.save()

        device = FCMDevice.objects.filter(user_id=rateReview_comment.rate_review.id).last()

        if device:
            device.send_message(title='TurtleBeans', body=str(rateReview_comment.user.first_name) + ' ' + str(rateReview_comment.user.last_name) + ' commented on the ' + str(rateReview_comment.rate_review.coffee.name) + ' product.')

            create_notification = Notifications.objects.create(
            user_id=self.request.user.id,
            Notification_image_id=NotificationsImages.objects.get(type='rate_review').id,
            title='TurtleBeans',
            body='You just got a reply on the ' + str(rateReview_comment.rate_review.coffee.name) + ' product.',
            type='rate_review')
        return Response(data={'result':True})
