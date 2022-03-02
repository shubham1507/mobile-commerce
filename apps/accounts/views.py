from django.shortcuts import render
from django.contrib.auth import authenticate
from django.db.models import Count, ExpressionWrapper, F, Sum, Q
from rest_framework import status, views, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken as OriginalObtain
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from .permissions import BaseUserPermission
from django.http import HttpResponse, JsonResponse
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import list_route, detail_route
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from . import serializers
from rauth import OAuth2Service
import braintree
from threading import Thread
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from bs4 import BeautifulSoup
from urllib.request import urlopen

from .models import EmailUser, Country, State, City, AppVersion
from .serializers import (AuthTokenSerializer, EmailUserSerializer,
                          CreateEmailUserSerializer, UpdateUserInfoSerializer,
                          CountrySerializer, StateSerializer, CitySerializer,
                          AppVersionSerializer)
from apps.orders.models import Cart, OrderPlaced, OrderPlacedMappig
from apps.coffee.models import Coffee
from apps.notifications.models import Notifications, NotificationsImages
from apps.contacts.models import Message
from fcm_django.models import FCMDevice
import paypalrestsdk
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from apps.coffee.models import CoffeeGrindTypes

import datetime

EMAILUSER_VALUES = [
    'id', 'first_name', 'last_name', 'email', 'birth_date', 'phone_number',
    'postal_code', 'country', 'state', 'city', 'ABN', 'timestamp',
    'company_name', 'profile_description', 'company_logo', 'background_image',
    'address_line_1', 'address_line_2', 'validated_at', 'is_seller',
    'is_buyer', 'is_terms_conditions_accepted', 'is_superuser',
    'is_notification_sound', 'is_notification_vibrate'
]


# Create your views here.
class GenericErrorResponse(Response):
    def __init__(self, message):
        # Ensure that the message always gets to the user in a standard format.
        if isinstance(message, ValidationError):
            message = message.detail
        if isinstance(message, str):
            message = [message]
        super().__init__({"non_field_errors": message}, status=400)


class ObtainAuthToken(OriginalObtain):
    def post(self, request, require_validated=True):
        serializer_class = AuthTokenSerializer
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.validated_data['user']
        except Exception as e:
            return Response(data={'errorMessage': serializer.validated_data},
                            status=200)
        token, created = Token.objects.get_or_create(user=user)
        notification_user = FCMDevice.objects.filter(user_id=user.id).update(
            active=False)
        crate_notification_user = FCMDevice.objects.create(
            # registration_id=self.request.data['registration_id'],
            registration_id='121111111',
            user_id=user.id,
            type=self.request.data['type'])
        return Response({
            'result': 'success',
            'email': user.email,
            'is_seller': user.is_seller,
            'is_buyer': user.is_buyer,
            'token': token.key,
            'id': user.id
        })


obtain_auth_token = ObtainAuthToken.as_view()


class EmailUserViewSet(viewsets.ModelViewSet):
    print("EmailUserViewSet has been called")
    serializer_class = EmailUserSerializer
    permission_classes = (IsAuthenticated, )
    queryset = EmailUser.objects.all()

    def get_queryset(self):# why its called twice on http://127.0.0.1:8000/api/users/
        q = self.queryset
       
        if 'email' in self.request.query_params:

            return q.filter(email=self.request.query_params['email'])
        return q.all()

    @list_route(methods=['POST'])
    def check_registered(self, request):
        
        if 'user_id' in request.data:
            user_data = []
            user_data_dir = {}
            user_details = EmailUser.objects.get(id=request.data['user_id'])
            user = EmailUser.objects.filter(id=request.data['user_id']).values(
                *EMAILUSER_VALUES)

            notifications = Notifications.objects.filter(
                user_id=request.user.id).filter(is_read=False)
            try:
                user_data_dir['company_logo'] = request.build_absolute_uri(
                    user_details.company_logo.url)
            except Exception as e:
                user_data_dir['company_logo'] = None

            try:
                user_data_dir['background_image'] = request.build_absolute_uri(
                    user_details.background_image.url)
            except Exception as e:
                user_data_dir['background_image'] = None

            try:
                user_data_dir['user_image'] = request.build_absolute_uri(
                    user_details.image.url)
            except Exception as e:
                user_data_dir['user_image'] = None

            user_data_dir['user'] = user

            try:
                user_data_dir['country_id'] = request.user.country.id
            except Exception as e:
                user_data_dir['country_id'] = None
            try:
                user_data_dir['country_name'] = request.user.country.name
            except Exception as e:
                user_data_dir['country_name'] = None
            try:
                user_data_dir['state_name'] = request.user.state.name
            except Exception as e:
                user_data_dir['state_name'] = None
            try:
                user_data_dir['city_name'] = request.user.city.name
            except Exception as e:
                user_data_dir['city_name'] = None
            user_data_dir['cartCount'] = Cart.objects.filter(
                buyer_id=request.data['user_id']).filter(
                    coffee__status=True).filter(
                        coffee__is_sold_out=False).count()
            user_data_dir['notificationsCount'] = notifications.count()
            user_data_dir['messageCount'] = Message.objects.filter(
                received_to=request.user.id).filter(is_read=False).count()
            user_data_dir['is_social'] = request.user.is_social
            user_data_dir[
                'is_seller_approved'] = request.user.is_seller_approved
            user_data.append(user_data_dir)
            user_data_dir = {}
            return Response(user_data)
        return Response('false')


class CreateEmailUserViewSet(viewsets.ModelViewSet):
    serializer_class = CreateEmailUserSerializer
    permission_classes = (AllowAny, )
    queryset = EmailUser.objects.all()

    def get_queryset(self):
        print("get_queryset has been called")
        q = self.queryset
        return q.all()

    def create(self, validated_data):
        print("create")
        if 'is_social' in self.request.data:

            pass
            # try:
            #     pass
            #     user = EmailUser.objects.get(email=self.request.data['email'])
            #     return JsonResponse({
            #         'id': user.id,
            #         'first_name': user.first_name,
            #         'last_name': user.last_name,
            #         'email': user.email,
            #         'is_seller': user.is_seller,
            #         'is_buyer': user.is_buyer,
            #         'token': user.auth_token.key,
            #         'validated_at': user.validated_at
            #     })
            
            # except Exception as e:
            #     print("except")
            #     user = self.create_user_api(validated_data)
            #     user.is_social = True
            #     user.validated_at = datetime.datetime.now()
            #     user.save()
            #     return Response(
            #         data={
            #             'id': user.id,
            #             'token': user.auth_token.key,
            #             'email': user.email,
            #             'is_seller': user.is_seller,
            #             'is_buyer': user.is_buyer,
            #             'validated_at': user.validated_at
            #         })
        
        else:
            user = self.create_user_api(validated_data)
            if user == False:
                user = EmailUser.objects.filter(
                    email=self.request.data['email'])
                if user:
                    return Response(
                        data={'result': 'Email id is already exist.'})
            return Response(
                data={
                    'id': user.id,
                    'token': user.auth_token.key,
                    'email': user.email,
                    'is_seller': user.is_seller,
                    'is_buyer': user.is_buyer,
                    'validated_at': user.validated_at
                })

    def create_user_api(self, validated_data):
        print("create_user_api")
        serializer = serializers.CreateEmailUserSerializer(
            data=self.request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return False
        user = serializer.save()
        user.set_password(self.request.data['password'])
        user.country_id = user.company_country_id
        user.save()
        if user.is_seller == True:
            user.is_seller_approved = True
            user.save()
        crate_notification_user = FCMDevice.objects.create(
            # registration_id=self.request.data['registration_id'],
            registration_id='111111111',
            # device_id=self.request.data['device_id'],
            device_id='1111111111',
            user_id=user.id,
            type="reminder")
        self.send_registration_email()
        return user

    def send_registration_email(self):
        print("send_registration_email")
        plaintext = get_template('registration_confirmation.txt')
        htmly = get_template('registration_confirmation.html')

        d = {'email': self.request.user}

        subject, from_email, to = 'Welcome', settings.DEFAULT_FROM_EMAIL, str(
            self.request.data['email'])
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class UpdateEmailUserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = UpdateUserInfoSerializer
    queryset = EmailUser.objects.all()

    @list_route(methods=['POST'])
    def updates(self, request, *args, **kwargs):
        user_obj = self.queryset.filter(email=request.data['email']).first()
        serializer = serializers.UpdateUserInfoSerializer(instance=user_obj,
                                                          data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if 'is_seller' in request.data:
            if request.data['is_seller'] == "True":
                user.is_seller_approved = True
        if 'new_state' in request.data:
            if request.data['new_state'] != "None" and request.data[
                    'new_state'] != '':
                state = State.objects.create(
                    name=request.data['new_state'],
                    country_id=request.data['country'])
            if request.data['new_city'] != "None" and request.data[
                    'new_city'] != '':
                city = City.objects.create(
                    name=request.data['new_city'],
                    state_id=state.id,
                    country_id=request.data['country'],
                    postcode=request.data['postal_code'])
                user.state = state
                user.city = city
                user.save()
        user.save()
        return Response({
            'id': user.id,
            'token': user.auth_token.key,
            'is_seller': user.is_seller,
            'is_buyer': user.is_buyer,
            'validated_at': user.validated_at
        })

    def send_invoice(self, mapping_id):
        orderPlaced_mapping = OrderPlacedMappig.objects.get(id=mapping_id)

        plaintext = get_template('invoice/index.txt')
        htmly = get_template('invoice/index.html')

        buyer_delivery_details = OrderPlaced.objects.filter(
            order_placed_mapping_id=mapping_id)[0].shipping

        orders = OrderPlaced.objects.filter(
            order_placed_mapping_id=mapping_id).annotate(
                coffee_name=F('coffee__name'),
                seller_email=F('seller__email'),
                grind=F('selected_grind__grind')).values(
                    'coffee_name', 'weight', 'qty', 'price', 'seller_email',
                    'grind')

        subtotal = orders.aggregate(Sum('price'))

        d = {
            'orders':
            orders,
            'subtotal':
            subtotal['price__sum'],
            'total':
            orderPlaced_mapping.price,
            'coupon_code':
            orderPlaced_mapping.coupon_code,
            'coupon_discount_amount':
            orderPlaced_mapping.coupon_discount_amount,
            'invoice_no':
            mapping_id,
            'buyer_name':
            self.request.user.first_name + ' ' + self.request.user.last_name,
            'address':
            buyer_delivery_details.address_line_1,
            'postcode':
            buyer_delivery_details.postal_code,
            'city':
            buyer_delivery_details.city.name,
            'state':
            buyer_delivery_details.state.name,
            'country':
            buyer_delivery_details.country.name,
            'contact_no':
            buyer_delivery_details.phone_number,
            'buyer_email':
            self.request.user.email,
            'date_of_invoice':
            OrderPlacedMappig.objects.get(id=mapping_id).timestamp.date(),
            'payment_symbol':
            self.request.user.country.currency_symbol
        }

        # seller_mail_list = []
        # orders_mails = orders.values_list('seller_email').distinct()
        # for mail in orders_mails:
        #     seller_mail_list.append(mail[0])

        subject, from_email, to = 'Invoice', settings.DEFAULT_FROM_EMAIL, self.request.user.email
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(subject,
                                     text_content,
                                     from_email, [to],
                                     bcc=[settings.ADMINS])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        sellers = orders.values_list('seller_id', 'seller_email').distinct()
        for seller in sellers:
            order1 = OrderPlaced.objects.filter(
                order_placed_mapping_id=mapping_id, seller=seller[0]).annotate(
                    coffee_name=F('coffee__name'),
                    seller_email=F('seller__email'),
                    grind=F('selected_grind__grind')).values(
                        'coffee_name', 'weight', 'qty', 'price',
                        'seller_email', 'grind')

            d = {
                'orders':
                order1,
                'subtotal':
                subtotal['price__sum'],
                'total':
                orderPlaced_mapping.price,
                'coupon_code':
                orderPlaced_mapping.coupon_code,
                'coupon_discount_amount':
                orderPlaced_mapping.coupon_discount_amount,
                'invoice_no':
                mapping_id,
                'buyer_name':
                self.request.user.first_name + ' ' +
                self.request.user.last_name,
                'address':
                buyer_delivery_details.address_line_1,
                'postcode':
                buyer_delivery_details.postal_code,
                'city':
                buyer_delivery_details.city.name,
                'state':
                buyer_delivery_details.state.name,
                'country':
                buyer_delivery_details.country.name,
                'contact_no':
                buyer_delivery_details.phone_number,
                'buyer_email':
                self.request.user.email,
                'date_of_invoice':
                OrderPlacedMappig.objects.get(id=mapping_id).timestamp.date(),
                'payment_symbol':
                self.request.user.country.currency_symbol
            }

            plaintext = get_template('invoice/seller_invoice.txt')
            htmly = get_template('invoice/seller_invoice.html')
            # seller_mail_list.append(settings.ADMINS)

            subject, from_email, to = 'New Order', settings.DEFAULT_FROM_EMAIL, seller[
                1]
            text_content = plaintext.render(d)
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject,
                                         text_content,
                                         from_email, [to],
                                         bcc=[settings.ADMINS])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        return Response('success')

    @list_route(methods=['POST'])
    def usd_cof_value(self, request, *args, **kwargs):
        try:
            cof_usd_page = 'https://www.livecoinwatch.com/price/CoffeeCoinUtilityToken-COF'
            page = urlopen(cof_usd_page)
            soup = BeautifulSoup(page, 'html.parser')
            name_box = soup.find('div', attrs={'class': 'content colored'})
            name_box = str(name_box).split('<div ')[2]
            name_box = name_box.split('$')[1]
            name_box = name_box.split('<')
            usd = float(name_box[0].strip())

            if not isinstance(usd, float):
                subject, from_email, to = 'COF Scraping code Errors', settings.DEFAULT_FROM_EMAIL, [
                    'vijendra@tersesoft.com'
                ]
                msg = EmailMultiAlternatives(subject, 'sjdklfjsj', from_email,
                                             to)
                msg.attach_alternative(
                    "Your COF scraping code is not working. Please check it...",
                    "text/html")
                msg.send()

                file = open("COF_price.txt", "r")
                usd = file.read()
                destination_address = settings.COF_DESTINATION_ADDRESS
                return Response(data={
                    'cof': float(usd),
                    'destination_address': destination_address
                })

    #previous code----->
    # cof_usd_page = 'https://coinranking.com/coin/coffeecoin-cof'
    # page = urlopen(cof_usd_page)
    # soup = BeautifulSoup(page, 'html.parser')
    # name_box = soup.find('span', attrs={'class': 'price__value'})
    # name_box = str(name_box).split('</span> ')
    # name_box =  name_box[1].split('<span>')[0]
    # name_box = name_box.split('<span')[0]
    # usd = float(name_box.strip())

            else:
                file = open("COF_price.txt", "w+")
                file.write(str(usd))
                file.close
                destination_address = settings.COF_DESTINATION_ADDRESS
                return Response(data={
                    'cof': usd,
                    'destination_address': destination_address
                })
        except:
            subject, from_email, to = 'COF Scraping code Errors', settings.DEFAULT_FROM_EMAIL, [
                'vijendra@tersesoft.com'
            ]
            msg = EmailMultiAlternatives(subject, 'sjdklfjsj', from_email, to)
            msg.attach_alternative(
                "Your COF scraping code is not working. Please check it...",
                "text/html")
            msg.send()

            file = open("COF_price.txt", "r")
            usd = file.read()
            destination_address = settings.COF_DESTINATION_ADDRESS
            return Response(data={
                'cof': float(usd),
                'destination_address': destination_address
            })

    def order_placed_handled(self):
        user = self.request.user
        cart_coffee = Cart.objects.filter(
            coffee_id__in=self.request.data['coffee_ids']).filter(
                buyer_id=user.id).delete()

        if 'cof_payment' in self.request.data:
            if 'coupon_code' in self.request.data:
                order_placed_mapping = OrderPlacedMappig.objects.create(
                    user_id=user.id,
                    price=self.request.data['amount'],
                    coupon_code=self.request.data['coupon_code'],
                    coupon_discount_amount=self.request.
                    data['coupon_discount_amount'],
                    attachment=self.request.data['attachment'])
            else:
                order_placed_mapping = OrderPlacedMappig.objects.create(
                    user_id=user.id,
                    price=self.request.data['amount'],
                    attachment=self.request.data['attachment'])
        else:
            config = braintree.BraintreeGateway(
                braintree.Configuration(
                    braintree.Environment.Production,
                    merchant_id=settings.BRAINTREE_MERCHANT_ID,
                    public_key=settings.BRAINTREE_PUBLIC_KEY,
                    private_key=settings.BRAINTREE_PRIVATE_KEY))

            paymet = config.transaction.sale({
                "amount":
                self.request.data['amount'],
                "merchant_account_id":
                str(self.request.user.country.braintree_merchanr_id),
                "payment_method_nonce":
                str(self.request.data['payment_method_nonce']),
                "options": {
                    "submit_for_settlement": True
                }
            })

            if 'coupon_code' in self.request.data:
                order_placed_mapping = OrderPlacedMappig.objects.create(
                    user_id=user.id,
                    price=self.request.data['amount'],
                    coupon_code=self.request.data['coupon_code'],
                    coupon_discount_amount=self.request.
                    data['coupon_discount_amount'])
            else:
                order_placed_mapping = OrderPlacedMappig.objects.create(
                    user_id=user.id, price=self.request.data['amount'])

        firstOrderPlaced = OrderPlaced.objects.filter(buyer_id=user.id)
        seller_ids = []
        for coffee_details in self.request.data['coffee_object']:
            coffee = Coffee.objects.get(id=coffee_details['coffee_id'])
            if coffee.seller_id not in seller_ids:
                seller_ids.append(coffee.seller_id)

            if 'cof_payment' in self.request.data:
                orderPlaced_coffee = OrderPlaced.objects.create(
                    buyer_id=user.id,
                    seller_id=coffee.seller_id,
                    coffee_id=coffee.id,
                    order_placed_mapping_id=order_placed_mapping.id,
                    selected_grind=CoffeeGrindTypes.objects.get(
                        id=coffee_details['selected_grind']),
                    weight=coffee_details['weight'],
                    qty=coffee_details['qty'],
                    price=coffee_details['price'],
                    shipping_id=self.request.data['shipping_id'],
                    shipping_charges=self.request.data['shipping_charges'])
            else:
                orderPlaced_coffee = OrderPlaced.objects.create(
                    buyer_id=user.id,
                    seller_id=coffee.seller_id,
                    coffee_id=coffee.id,
                    order_placed_mapping_id=order_placed_mapping.id,
                    selected_grind=CoffeeGrindTypes.objects.get(
                        id=coffee_details['selected_grind']),
                    braintree_translation_id=paymet.transaction.id,
                    weight=coffee_details['weight'],
                    qty=coffee_details['qty'],
                    price=coffee_details['price'],
                    shipping_id=self.request.data['shipping_id'],
                    shipping_charges=self.request.data['shipping_charges'])

        device = FCMDevice.objects.filter(user_id=user.id).filter(active=True)
        if 'cof_payment' in self.request.data:
            if len(firstOrderPlaced) == 0:
                device.send_message(
                    title="TurtleBeans",
                    body=
                    "Congratulations you have just placed your first product using COF. Your payment is under process."
                )
                create_notification = Notifications.objects.create(
                    user_id=user.id,
                    Notification_image_id=NotificationsImages.objects.get(
                        type='first_order').id,
                    title='TurtleBeans',
                    body='Congratulations you just brought your first product.',
                    type='first_order')
        else:
            if len(firstOrderPlaced) == 0:
                device.send_message(
                    title="TurtleBeans",
                    body="Congratulations you just brought your first product."
                )
                create_notification = Notifications.objects.create(
                    user_id=user.id,
                    Notification_image_id=NotificationsImages.objects.get(
                        type='first_order').id,
                    title='TurtleBeans',
                    body='Congratulations you just brought your first product.',
                    type='first_order')

        if 'cof_payment' in self.request.data:
            device.send_message(
                title="TurtleBeans",
                body=
                "Thanks for purchasing with Turtlebeans! your fresh roast will be with you soon. Please check your email for more information. Your payment is under process."
            )
            create_notification = Notifications.objects.create(
                user_id=user.id,
                Notification_image_id=NotificationsImages.objects.get(
                    type='order_placed').id,
                title='TurtleBeans',
                body=
                "Thanks for purchasing with Turtlebeans! your fresh roast will be with you soon. Please check your email for more information. Your payment is under process.",
                type='order_placed')

            # device = FCMDevice.objects.filter(user_id__in=seller_ids).filter(active=True)
            # device.send_message(title="TurtleBeans", body="It's time to roast! Order No: "+ str(order_placed_mapping.id)+" has just been made. Please check your email for more information. Your payment is under process.")
            # create_notification = Notifications.objects.create(
            # user_id=coffee.seller.id,
            # Notification_image_id=NotificationsImages.objects.get(type='order_placed').id,
            # title='TurtleBeans',
            # body="It's time to roast! Order No: "+ str(order_placed_mapping.id)+" has just been made. Please check your email for more information. Your payment is under process.",
            # type='order_placed')

            plaintext = get_template('email/COF_pending_order.txt')
            htmly = get_template('email/COF_pending_order.html')
            d = {
                'order': 'cof new pending order',
                'order_number': order_placed_mapping.id,
                'payment_symbol': 'COF'
            }

            subject, from_email, to = 'COF pending order', settings.DEFAULT_FROM_EMAIL, settings.ADMINS
            text_content = plaintext.render(d)
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, text_content, from_email,
                                         [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            device.send_message(
                title="TurtleBeans",
                body=
                "Thanks for purchasing with Turtlebeans! your fresh roast will be with you soon. Please check your email for more information."
            )
            create_notification = Notifications.objects.create(
                user_id=user.id,
                Notification_image_id=NotificationsImages.objects.get(
                    type='order_placed').id,
                title='TurtleBeans',
                body=
                "Thanks for purchasing with Turtlebeans! your fresh roast will be with you soon. Please check your email for more information.",
                type='order_placed')

            device = FCMDevice.objects.filter(user_id__in=seller_ids).filter(
                active=True)
            device.send_message(
                title="TurtleBeans",
                body="It's time to roast! Order No: " +
                str(order_placed_mapping.id) +
                " has just been made. Please check your email for more information."
            )
            create_notification = Notifications.objects.create(
                user_id=coffee.seller.id,
                Notification_image_id=NotificationsImages.objects.get(
                    type='order_placed').id,
                title='TurtleBeans',
                body="It's time to roast! Order No: " +
                str(order_placed_mapping.id) +
                " has just been made. Please check your email for more information.",
                type='order_placed')

        if 'cof_payment' not in self.request.data:
            mapping_id = order_placed_mapping.id
            self.send_invoice(mapping_id)
        return Response(data={'result': True})

    @list_route(methods=['POST'])
    def create_braintree_customer(self, request):
        user = request.user
        f = open("post_requst_data.txt", "a")
        f.write("{}\n".format(request.data))
        if 'cof' in request.data:
            if 'cof_payment' not in request.data:
                attachment = get_random_string(length=10)
                return Response(data={'attachment': attachment})
            if 'cof_payment' in request.data:
                self.order_placed_handled()

        if 'payment_method_nonce' in request.data:
            self.order_placed_handled()

        if 'cof' not in request.data:
            config = braintree.BraintreeGateway(
                braintree.Configuration(
                    braintree.Environment.Production,
                    merchant_id=settings.BRAINTREE_MERCHANT_ID,
                    public_key=settings.BRAINTREE_PUBLIC_KEY,
                    private_key=settings.BRAINTREE_PRIVATE_KEY))

            if user.braintree_customer_id is None:
                create_customer = config.customer.create({
                    "email":
                    request.user.email,
                    "first_name":
                    request.user.first_name,
                    "last_name":
                    request.user.last_name
                })

                user.braintree_customer_id = create_customer.customer.id
                user.save()

            client_token = config.client_token.generate(
                {"customer_id": user.braintree_customer_id})
            return Response(data={'client_token': client_token})
        return Response(data={'result': True})


class UpdateUserImageViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny, )
    serializer_class = UpdateUserInfoSerializer
    queryset = EmailUser.objects.all()

    @list_route(methods=['POST'])
    def update_image(self, request, *args, **kwargs):
        if 'images' in request.FILES:
            images = request.FILES.getlist('images')

            try:
                user = EmailUser.objects.get(email=request.data['email'])
                if user:
                    for image in images:
                        user.image = image
                        user.save()
            except Exception as e:
                return Response(data={'result': False})

        if 'company_logos' in request.FILES:
            company_logos = request.FILES.getlist('company_logos')
            try:
                user = EmailUser.objects.get(email=request.data['email'])
                if user:
                    for company_logo in company_logos:
                        user.company_logo = company_logo
                        user.save()
            except Exception as e:
                return Response(data={'result': False})

        if 'background_images' in request.FILES:
            background_images = request.FILES.getlist('background_images')
            try:
                user = EmailUser.objects.get(email=request.data['email'])
                if user:
                    for background_image in background_images:
                        user.background_image = background_image
                        user.save()
            except Exception as e:
                return Response(data={'result': False})

        return Response(data={'id': user.id})


class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    permission_classes = (AllowAny, )
    queryset = Country.objects.order_by('name')
    pagination_class = None

    def get_queryset(self):
        q = self.queryset
        return q.all()


class StateViewSet(viewsets.ModelViewSet):
    serializer_class = StateSerializer
    permission_classes = (IsAuthenticated, )
    queryset = State.objects.all()

    def get_queryset(self):
        q = self.queryset
        if 'country_id' in self.request.query_params:
            return q.filter(country=self.request.query_params['country_id'])
        return q.all()


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    permission_classes = (IsAuthenticated, )
    queryset = City.objects.all()

    def get_queryset(self):
        q = self.queryset
        if 'country_id' in self.request.query_params and 'state_id' in self.request.query_params:
            return q.filter(
                country=self.request.query_params['country_id']).filter(
                    state=self.request.query_params['state_id'])
        return q.all()

    @list_route(methods=['POST'])
    def postcode_details(self, request):
        location_list = []
        location_dir = {}
        user = EmailUser.objects.get(email=request.user.email)
        if 'buyer' in request.data:
            location_dir['city'] = City.objects.filter(
                postcode__exact=request.data['postcode']).filter(
                    country__group_country_id=user.country.group_country_id
                ).values()
        else:
            try:
                location_dir['city'] = City.objects.filter(
                    postcode__exact=request.data['postcode']).filter(
                        country_id=request.data['country_id']).values()
            except Exception as e:
                location_dir['city'] = City.objects.filter(
                    postcode__exact=request.data['postcode']).values()
        if location_dir['city']:
            location_dir['state'] = State.objects.filter(
                id=location_dir['city'][0]['state_id']).values()
            location_dir['Country'] = Country.objects.filter(
                id=location_dir['state'][0]['country_id']).values()
            location_list.append(location_dir)
            location_dir = {}
        else:
            location_list = []
        return Response(location_list)


class ChangePassword(views.APIView):
    """View for entering and re-entering a new password. """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, *args, **kwargs):
        key = self.request.data.get('token')
        user = get_object_or_404(Token, key=key).user
        pw1 = self.request.data.get('pw1')
        pw2 = self.request.data.get('pw2')
        user = authenticate(email=self.request.data.get('email'), password=pw1)
        if user is None:
            return Response(data={
                'result': False,
                'message': "Current password is not matched!"
            },
                            status=200)
        if user is not None and (pw1 and pw2):
            user.set_password(pw2)
            user.save()
            return Response(data={
                'result': True,
                'message': 'Password updated successfully.'
            },
                            status=status.HTTP_202_ACCEPTED)
        return Response(data={
            'result': False,
            'message': "Missing/Not Matching Passwords"
        },
                        status=200)


class ValidateUserView(TemplateView):
    """
    User validation link routs to this view, notifying success.
    If user has already validated, this view will 404.
    """
    template_name = 'validation/validate.html'

    def get_context_data(self, **kwargs):
        validation_key = kwargs.get('validation_key')
        user = get_object_or_404(get_user_model(),
                                 validation_key=validation_key)
        user.validate()
        try:
            company_country_name = user.company_country.name
        except:
            company_country_name = None
        try:
            company_name = user.company_name
        except:
            company_name = None

        if user.is_seller:
            d = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'company_country_name': company_country_name,
                'phone_number': user.phone_number,
                'company_name': company_name,
                'business_registration_number': user.ABN
            }

            htmly = get_template('validation/new_seller.html')

            subject, from_email, to = 'New Seller', settings.DEFAULT_FROM_EMAIL, settings.ADMINS
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email,
                                         [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()


class RequestPasswordChange(views.APIView):
    """
    Retrieves the user by email, and emails them a reset password link.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        email = kwargs.get('email')
        try:
            user = EmailUser.objects.get(email=email)
        except Exception as e:
            return Response(data={'result': False})
        user.send_reset_password_email(request)
        # 202 : we've accepted the request, but user must complete the process.
        return Response(data={'result': True}, status=status.HTTP_202_ACCEPTED)


class AppVersionViewSet(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        version = AppVersion.objects.filter(status=True).values()
        return Response(version)


def cof_send_invoice(mapping_id):
    orderPlaced_mapping = OrderPlacedMappig.objects.get(id=mapping_id)
    if orderPlaced_mapping.attachment != '':
        plaintext = get_template('invoice/index.txt')
        htmly = get_template('invoice/index.html')

        buyer_delivery_details = OrderPlaced.objects.filter(
            order_placed_mapping_id=mapping_id)[0].shipping

        orders = OrderPlaced.objects.filter(
            order_placed_mapping_id=mapping_id).annotate(
                coffee_name=F('coffee__name'),
                seller_email=F('seller__email'),
                grind=F('selected_grind__grind')).values(
                    'coffee_name', 'weight', 'qty', 'price', 'seller_email',
                    'seller', 'grind')

        buyer_details = OrderPlaced.objects.filter(
            order_placed_mapping_id=mapping_id).first().buyer
        buyer_first_name = buyer_details.first_name
        buyer_last_name = buyer_details.last_name
        buyer_email = buyer_details.email

        subtotal = orders.aggregate(Sum('price'))
        d = {
            'orders':
            orders,
            'subtotal':
            subtotal['price__sum'],
            'total':
            orderPlaced_mapping.price,
            'coupon_code':
            orderPlaced_mapping.coupon_code,
            'coupon_discount_amount':
            orderPlaced_mapping.coupon_discount_amount,
            'invoice_no':
            mapping_id,
            'buyer_name':
            buyer_first_name + ' ' + buyer_last_name,
            'address':
            buyer_delivery_details.address_line_1,
            'postcode':
            buyer_delivery_details.postal_code,
            'city':
            buyer_delivery_details.city.name,
            'state':
            buyer_delivery_details.state.name,
            'country':
            buyer_delivery_details.country.name,
            'buyer_email':
            buyer_email,
            'date_of_invoice':
            OrderPlacedMappig.objects.get(id=mapping_id).timestamp.date(),
            'payment_symbol':
            'COF'
        }

        subject, from_email, to = 'Invoice', settings.DEFAULT_FROM_EMAIL, buyer_email
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(subject,
                                     text_content,
                                     from_email, [to],
                                     bcc=[settings.ADMINS])
        #msg = EmailMultiAlternatives(subject, text_content, from_email, ['vijendra@tersesoft.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        sellers = orders.values_list('seller_id', 'seller_email').distinct()
        for seller in sellers:
            order1 = OrderPlaced.objects.filter(
                order_placed_mapping_id=mapping_id, seller=seller[0]).annotate(
                    coffee_name=F('coffee__name'),
                    seller_email=F('seller__email'),
                    grind=F('selected_grind__grind')).values(
                        'coffee_name', 'weight', 'qty', 'price',
                        'seller_email', 'grind')

            d = {
                'orders':
                order1,
                'subtotal':
                subtotal['price__sum'],
                'total':
                orderPlaced_mapping.price,
                'coupon_code':
                orderPlaced_mapping.coupon_code,
                'coupon_discount_amount':
                orderPlaced_mapping.coupon_discount_amount,
                'invoice_no':
                mapping_id,
                'buyer_name':
                buyer_first_name + ' ' + buyer_last_name,
                'address':
                buyer_delivery_details.address_line_1,
                'postcode':
                buyer_delivery_details.postal_code,
                'city':
                buyer_delivery_details.city.name,
                'state':
                buyer_delivery_details.state.name,
                'country':
                buyer_delivery_details.country.name,
                'buyer_email':
                buyer_email,
                'date_of_invoice':
                OrderPlacedMappig.objects.get(id=mapping_id).timestamp.date(),
                'payment_symbol':
                'COF'
            }

            plaintext = get_template('invoice/seller_invoice.txt')
            htmly = get_template('invoice/seller_invoice.html')

            subject, from_email, to = 'New Order', settings.DEFAULT_FROM_EMAIL, seller[
                1]
            text_content = plaintext.render(d)
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject,
                                         text_content,
                                         from_email, [to],
                                         bcc=[settings.ADMINS])
            #msg = EmailMultiAlternatives(subject, text_content, from_email, ['vijendra@tersesoft.com'])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
