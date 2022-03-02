from django.shortcuts import render
from .models import Version
from rest_framework import viewsets
from .serializers import VersionSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.


class VersionViewSet(viewsets.ModelViewSet):
    serializer_class = VersionSerializer
    permission_classes = (AllowAny,)
    queryset = Version.objects.all()

    def get_queryset(self):
        q = self.queryset
        return q.all()
