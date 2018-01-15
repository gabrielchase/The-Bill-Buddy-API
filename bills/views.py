from django.shortcuts import render

from rest_framework import viewsets

from bills.models import Bill
from bills.serializers import BillSerializer


class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    # authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (UserPermission,)


