from django.contrib.auth import get_user_model

from rest_framework import serializers

from payments.models import Payment

import json

User = get_user_model()


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ('id', 'amount', 'date', 'status', 'additional_notes', 'bill', 'user')
