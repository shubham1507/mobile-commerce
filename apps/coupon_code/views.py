from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import list_route, detail_route
from django.utils import timezone

from .models import Coupon
from .serializers import CouponSerializer
# Create your views here.

class CouponViewSet(viewsets.ModelViewSet):
    serializer_class = CouponSerializer
    permission_classes = (AllowAny,)
    queryset = Coupon.objects.all()

    def get_queryset(self):
        q = self.queryset
        return q.all()

    @list_route(methods=['POST'])
    def coupon_apply(self, request, *args, **kwargs):
        now = timezone.now()
        try:
            coupon = Coupon.objects.get(code__exact=request.data['code'],
                                        valid_from__lte=now,
                                        valid_to__gte=now,
                                        status=True)
            if coupon.percentage_discount != 0:
                return Response(data={'code':coupon.code, 'percentage_discount':coupon.percentage_discount})
            if coupon.flat_discount != 0:
                return Response(data={'code':coupon.code, 'flat_discount':coupon.flat_discount})
        except Coupon.DoesNotExist:
            return Response(data={'result':False})
