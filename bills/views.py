from django.shortcuts import render

from rest_framework import viewsets
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from bills.models import Bill
from bills.permissions import BillPermission
from bills.serializers import BillSerializer


class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (BillPermission,)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise ValueError('JWT not found in request headers')
        
        service_name = self.request.GET.get('service')
        bills = Bill.objects.filter(user=self.request.user)
        
        if service_name: 
            bills = bills.filter(service__name=service_name.title())

        return bills
        