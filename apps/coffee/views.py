from django.shortcuts import render
from django.db.models import F, Func, functions, Count, ExpressionWrapper, FloatField, Case, When, Q
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import list_route, detail_route
from .models import (CoffeeImages, PriceWithSize, Coffee, CoffeeWeight,
                     CoffeeQTY, CoffeeGrindTypes, CoffeeSelectedGrindTypes,
                     CoffeeLogos, Favourite)
from .serializers import (CoffeeImagesSerializer, PriceWithSizeSerializer,
                          CoffeeSerializer, CoffeeAddUpdateSerializer,
                          CoffeeWeightSerializer, CoffeeQTYSerializer,
                          CoffeeGrindTypesSerializer, CoffeeSelectedGrindTypes,
                          CoffeeLogosSerializer, FavouriteSerializer)
from apps.accounts.models import EmailUser, Country
from apps.orders.models import Cart, OrderPlaced
from . import serializers
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from urllib.request import urlopen
from bs4 import BeautifulSoup
from rest_framework.viewsets import (ModelViewSet, ReadOnlyModelViewSet,
                                     GenericViewSet)

COUNTRY_IDS = [
    1, 2, 3, 4, 14, 21, 49, 61, 64, 65, 70, 73, 88, 99, 105, 106, 113, 128,
    129, 144, 162, 163, 166, 169
]

# Create your views here.


class CoffeeImagesViewSet(viewsets.ModelViewSet):
    serializer_class = CoffeeImagesSerializer
    permission_classes = (AllowAny, )
    queryset = CoffeeImages.objects.all()

    def get_queryset(self):
        q = self.queryset
        return q.all()

    @list_route(methods=['POST'])
    def add_images(self, request, *args, **kwargs):

        if 'order_updates' in request.data:
            for order_update in request.data['order_updates']:
                coffeeImage = CoffeeImages.objects.get(
                    id=order_update['coffee_image_id'])
                coffeeImage.order = order_update['order']
                coffeeImage.save()
            return Response(data={'result': True})
        else:
            images = request.FILES.getlist('coffee_images')
            for image in images:
                coffee_image = CoffeeImages.objects.create(
                    coffee_id=request.data['coffee_id'],
                    image=image,
                    order=request.data['order'])
            return Response(data={
                'coffee_id': request.data['coffee_id'],
                'id': request.user.id,
                'coffee_image_id': coffee_image.id
            },
                            status=200)

    @list_route(methods=['POST'])
    def delete_image(self, request, *args, **kwargs):
        a = CoffeeImages.objects.filter(
            id=request.data['coffee_image_id'],
            coffee_id=request.data['coffee_id']).delete()
        return Response(data={'result': True})


class PriceWithSizeViewSet(viewsets.ModelViewSet):
    serializer_class = PriceWithSizeSerializer
    permission_classes = (IsAuthenticated, )
    queryset = PriceWithSize.objects.all()


class CoffeeViewSet(viewsets.ModelViewSet):
    serializer_class = CoffeeSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Coffee.objects.all()

    def get_queryset(self):

        user_check = EmailUser.objects.get(
            id=self.request.query_params['user_check_id'])

        user_country = user_check.country.group_country_id
        q = self.queryset.filter(
            seller__country__group_country_id=user_country).filter(status=True)
        inter_coffee = self.queryset.filter(
            inter_shipping_charge__isnull=False)
        if 'similar' in self.request.query_params:
            return q.filter(
                grind_id=self.request.query_params['grind_id']).filter(
                    seller__is_seller_approved=True).exclude(
                        id=self.request.query_params['coffee_id'])

        if 'coffee_id' in self.request.query_params and self.request.user.country_id in COUNTRY_IDS:
            return q.filter(id=self.request.query_params['coffee_id']).filter(
                seller__is_seller_approved=True)

        if 'latest' in self.request.query_params and 'seller_id' in self.request.query_params:
            return q.filter(
                seller_id=self.request.query_params['seller_id']).filter(
                    seller__is_seller_approved=True).order_by('-timestamp')

        if 'latest' in self.request.query_params and self.request.user.country_id in COUNTRY_IDS:
            return ((q.filter(
                seller__is_seller_approved=True).order_by('-timestamp')
                     ).union(inter_coffee)).distinct()

        if 'seller_id' in self.request.query_params and 'latest' not in self.request.query_params:
            return q.filter(
                seller_id=self.request.query_params['seller_id']).filter(
                    seller__is_seller_approved=True).order_by('timestamp')

        if 'cart_buyer_id' in self.request.query_params and self.request.user.country_id in COUNTRY_IDS:
            coffee_list = []
            cart = Cart.objects.filter(
                buyer_id=self.request.query_params['cart_buyer_id']).filter(
                    coffee__is_sold_out=False).order_by('-timestamp')
            for cart_product in cart:
                coffee = q.filter(id=cart_product.coffee_id).filter(
                    seller__is_seller_approved=True)
                coffee_list.append(coffee[0])
            return coffee_list

        if 'best_selling_products' in self.request.query_params and self.request.user.country_id in COUNTRY_IDS:
            orders = OrderPlaced.objects.values('coffee').annotate(
                counts=Count('coffee'),
                date__=timezone.now().date() + relativedelta(days=1) -
                Func(F('coffee__timestamp'), function='DATE')).annotate(
                    value=ExpressionWrapper(
                        F('counts') /
                        F('date__'), output_field=FloatField())).order_by(
                            '-value').values_list('coffee')
            q = q.filter(id__in=orders).filter(seller__is_seller_approved=True)
            q = [x for _, x in sorted(zip(orders, q))]
            return q

        if 'search' in self.request.query_params:
            search = self.request.query_params['search']
            if search:
                if ' ' not in search:
                    qs = q.filter(
                        Q(name__icontains=search)
                        | Q(coffee_from__icontains=search)
                        | Q(variety__icontains=search)
                        | Q(aroma__icontains=search)
                        | Q(description__icontains=search))
                    return qs
                elif ' ' in search:
                    words = search.split(' ')
                    if '' in words:
                        words.remove('')
                    if len(words) == 1:
                        first = search.split(' ')
                        qs = q.filter(
                            Q(name__icontains=first)
                            | Q(coffee_from__icontains=first)
                            | Q(variety__icontains=first)
                            | Q(aroma__icontains=first)
                            | Q(description__icontains=first))
                        return qs
                    if len(words) == 2:
                        qs = q.filter(
                            Q(name__icontains=words[0])
                            | Q(name__icontains=words[1])
                            | Q(coffee_from__icontains=words[0])
                            | Q(coffee_from__icontains=words[1])
                            | Q(variety__icontains=words[0])
                            | Q(variety__icontains=words[1])
                            | Q(aroma__icontains=words[0])
                            | Q(aroma__icontains=words[1])
                            | Q(description__icontains=words[0])
                            | Q(description__icontains=words[1]))
                        return qs
                    if len(words) == 3:
                        qs = q.filter(
                            Q(name__icontains=words[0])
                            | Q(name__icontains=words[1])
                            | Q(name__icontains=words[2])
                            | Q(coffee_from__icontains=words[0])
                            | Q(coffee_from__icontains=words[1])
                            | Q(coffee_from__icontains=words[2])
                            | Q(variety__icontains=words[0])
                            | Q(variety__icontains=words[1])
                            | Q(variety__icontains=words[2])
                            | Q(aroma__icontains=words[0])
                            | Q(aroma__icontains=words[1])
                            | Q(aroma__icontains=words[2])
                            | Q(description__icontains=words[0])
                            | Q(description__icontains=words[1])
                            | Q(description__icontains=words[2]))
                        return qs
        if 'buyer_id' in self.request.query_params and self.request.user.country_id in COUNTRY_IDS:
            favourites = Favourite.objects.filter(
                buyer_id=self.request.query_params['buyer_id']).values_list(
                    'coffee_id')
            return q.filter(id__in=favourites).filter(
                seller__is_seller_approved=True)
        if self.request.user.country_id in COUNTRY_IDS:
            return q.all().filter(seller__is_seller_approved=True)
        return []

    @list_route(methods=['POST'])
    def add_update(self, request, *args, **kwargs):
        if 'id' in request.data:
            coffee_obj = self.queryset.filter(id=request.data['id']).first()
            serializer = serializers.CoffeeAddUpdateSerializer(
                instance=coffee_obj, data=request.data)
            serializer.is_valid(raise_exception=True)
            coffee = serializer.save()

            if 'special_weights' in request.data:
                special_weights = request.data['special_weights']
                special_weights_delete = PriceWithSize.objects.filter(
                    coffee_id=coffee.id).delete()

                PriceWithSize.objects.create(
                    coffee_id=coffee.id,
                    weight_id=coffee.weight_id,
                    price=coffee.price,
                    shipping_charge=coffee.shipping_charge,
                    inter_shipping_charge=coffee.inter_shipping_charge)

                for special_weight in special_weights:
                    check_weight = PriceWithSize.objects.filter(
                        coffee_id=coffee.id,
                        weight_id=special_weight['weight_id'])
                    if check_weight:
                        continue
                    PriceWithSize.objects.create(
                        coffee_id=coffee.id,
                        weight_id=special_weight['weight_id'],
                        price=special_weight['price'],
                        shipping_charge=special_weight['shipping_charge'],
                        inter_shipping_charge=special_weight[
                            'inter_shipping_charge'])

            if 'special_grinds' in request.data:
                special_grinds = request.data['special_grinds']
                special_grinds_delete = CoffeeSelectedGrindTypes.objects.filter(
                    coffee_id=coffee.id).delete()
                for special_grind in special_grinds:
                    CoffeeSelectedGrindTypes.objects.create(
                        coffee_id=coffee.id, grind_id=special_grind)
            return Response(data={'coffee_id': coffee.id})
        else:
            serializer = serializers.CoffeeAddUpdateSerializer(
                data=request.data)
            serializer.is_valid(raise_exception=True)
            coffee = serializer.save()

            PriceWithSize.objects.create(
                coffee_id=coffee.id,
                weight_id=coffee.weight_id,
                price=coffee.price,
                shipping_charge=coffee.shipping_charge,
                inter_shipping_charge=coffee.inter_shipping_charge)
            special_weights = request.data['special_weights']
            for special_weight in special_weights:
                check_weight = PriceWithSize.objects.filter(
                    coffee_id=coffee.id, weight_id=special_weight['weight_id'])
                if check_weight:
                    continue
                PriceWithSize.objects.create(
                    coffee_id=coffee.id,
                    weight_id=special_weight['weight_id'],
                    price=special_weight['price'],
                    shipping_charge=special_weight['shipping_charge'],
                    inter_shipping_charge=special_weight[
                        'inter_shipping_charge'])
            special_grinds = request.data['special_grinds']
            for special_grind in special_grinds:
                CoffeeSelectedGrindTypes.objects.create(coffee_id=coffee.id,
                                                        grind_id=special_grind)
            return Response(data={'coffee_id': coffee.id})

    @list_route(methods=['POST'])
    def coffee_deactivate(self, request, *args, **kwargs):
        coffee = Coffee.objects.get(id=request.data['coffee_id'])
        coffee.status = False
        coffee.save()
        return Response(data={'result': coffee.id})

    @list_route(methods=['GET'])
    def coffee_converted_price(self, request):
        converted_prices = []
        prices = {}
        user_country_group_id = EmailUser.objects.get(
            id=self.request.query_params['user_check_id']
        ).country.group_country_id
        countries = Country.objects.filter(
            group_country_id=user_country_group_id)
        countries = countries.filter(id__in=COUNTRY_IDS)

        for country in countries:
            for another_country in countries:
                price_converter_page = 'https://www.x-rates.com/calculator/?from=' + str(
                    country.currency_symbol) + '&to=' + str(
                        another_country.currency_symbol) + '&amount=1'
                page = urlopen(price_converter_page)
                soup = BeautifulSoup(page, 'html.parser')
                name_box = soup.find('span', attrs={'class': 'ccOutputRslt'})
                prices['from_country_id'] = country.id
                prices['to_country_id'] = another_country.id
                if ',' in name_box.text.split(' ')[0].strip():
                    price = name_box.text.split(' ')[0].strip()
                    price = price.replace(',', '')
                    prices['converted_price'] = float(price)
                else:
                    prices['converted_price'] = float(
                        name_box.text.split(' ')[0].strip())
                converted_prices.append(prices)
                prices = {}
        return Response(converted_prices)

    @list_route(methods=['GET'])
    def usd_amount(self, request):
        user_country = EmailUser.objects.get(
            id=self.request.query_params['user_check_id']).country
        price_converter_page = 'https://www.x-rates.com/calculator/?from=' + str(
            user_country.currency_symbol) + '&to=USD&amount=1'
        page = urlopen(price_converter_page)
        soup = BeautifulSoup(page, 'html.parser')
        name_box = soup.find('span', attrs={'class': 'ccOutputRslt'})
        return Response(
            data={'usd_amount': float(name_box.text.split(' ')[0].strip())})


class CoffeeBgImageViewSet(viewsets.ModelViewSet):
    serializer_class = CoffeeSerializer
    permission_classes = (AllowAny, )
    queryset = Coffee.objects.all()

    @list_route(methods=['POST'])
    def add(self, request, *args, **kwargs):
        images = request.FILES.getlist('coffee_background_images')
        coffee = Coffee.objects.get(id=request.data['coffee_id'])
        if coffee:
            for image in images:
                coffee.background_image = image
                coffee.save()
        return Response(data={'id': coffee.id})


class CoffeeWeightViewSet(viewsets.ModelViewSet):
    serializer_class = CoffeeWeightSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None
    queryset = CoffeeWeight.objects.all()

    def get_queryset(self):
        q = self.queryset.filter(group_id=self.request.user.country.
                                 group_country_id).order_by('weight')
        return q.all()


class CoffeeQTYViewSet(viewsets.ModelViewSet):
    serializer_class = CoffeeQTYSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None
    queryset = CoffeeQTY.objects.all()


class CoffeeGrindTypesViewSet(viewsets.ModelViewSet):
    serializer_class = CoffeeGrindTypesSerializer
    permission_classes = (IsAuthenticated, )
    queryset = CoffeeGrindTypes.objects.all()


class CoffeeLogosViewSet(viewsets.ModelViewSet):
    serializer_class = CoffeeLogosSerializer
    permission_classes = (AllowAny, )
    queryset = CoffeeLogos.objects.all()

    def get_queryset(self):
        q = self.queryset
        return q.all()

    @list_route(methods=['POST'])
    def add_images(self, request, *args, **kwargs):
        images = request.FILES.getlist('coffee_logo_images')

        coffee_logos = CoffeeLogos.objects.filter(
            user_id=request.user.id).filter(
                coffee_id=request.data['coffee_id'])
        for image in images:
            if coffee_logos:
                coffee_logos.update(company_logo=image)
            else:
                CoffeeLogos.objects.create(user_id=request.data['user_id'],
                                           coffee_id=request.data['coffee_id'],
                                           company_logo=image)
        return Response(data={
            'coffee_id': request.data['coffee_id'],
            'id': request.user.id
        })


class FavouriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Favourite.objects.all()

    def get_queryset(self):
        q = self.queryset
        if 'buyer' in self.request.query_params:
            return q.filter(buyer_id=self.request.query_params['buyer'])
        return q.all()

    @list_route(methods=['POST'])
    def remove_favourite(self, request, *args, **kwargs):
        q = self.queryset
        remove_favourites = q.filter(buyer_id=request.data['buyer']).filter(
            coffee_id=request.data['coffee']).delete()
        return JsonResponse({'result': 'true'})
