from django.shortcuts import render

from rest_framework import (generics, viewsets)
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from bills.models import (Bill, Service)
from bills.permissions import (BillPermission, ServicePermission)
from bills.serializers import (BillSerializer, BillDetailSerializer, ServiceSerializer)


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

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BillDetailSerializer
        else:
            return BillSerializer
        

class ServiceList(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (ServicePermission,)

    def get_queryset(self):
        user_bills = self.request.user.bills.all()
        user_services = [bill.service for bill in user_bills]
        return set(user_services)
