from django.shortcuts import render

from rest_framework import viewsets
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from payments.models import Payment 
from payments.permissions import PaymentPermission
from payments.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (PaymentPermission,)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise ValueError('JWT not found in request headers')

        return Payment.objects.filter(user=self.request.user)
        