from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from bills.models import Bill
from payments.models import Payment

import json

User = get_user_model()


class PaymentSerializer(serializers.ModelSerializer):
    bill_id = serializers.IntegerField()
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'amount', 'due_date', 'date_paid', 'status', 'additional_notes', 'bill_id', 'user_id')

    def create(self, data):
        print('Creating new payment with data: ', data)
        
        try:
            bill_id = data.get('bill_id')
            print(bill_id)
            bill_instance = Bill.objects.get(id=bill_id)
            print(bill_instance)
            new_payment = Payment.objects.create(
                amount=data.get('amount'),
                due_date=data.get('due_date'),
                date_paid=data.get('date_paid'),
                status=data.get('status'),
                additional_notes=data.get('additional_notes'),
                bill=bill_instance,
                user=self.context['request'].user
            )
        except Bill.DoesNotExist:
            raise ValueError('Bill with id {} does not exist'.format(bill_id))

        print('New bill created: ', new_payment)
        
        return new_payment

    def update(self, payment_instance, data):
        del data['bill_id']

        payment_instance.amount = data.get('amount')
        payment_instance.due_date = data.get('due_date')
        payment_instance.date_paid = data.get('date_paid')
        payment_instance.status = data.get('status')
        payment_instance.additional_notes = data.get('additional_notes')
        payment_instance.save()
        return payment_instance
