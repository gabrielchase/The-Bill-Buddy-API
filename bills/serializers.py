from django.contrib.auth import get_user_model
from django.db.models import Sum

from rest_framework import serializers

from bills.models import (Bill, Service)
from bills.utils import handle_service_instance

from payments.models import Payment
from payments.serializers import PaymentSerializer

import json
import datetime

User = get_user_model()
TODAY = datetime.date.today()


class BillSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(read_only=True)
    service_id = serializers.IntegerField(read_only=True)
    instance_service_name = serializers.SerializerMethodField()
    service_name = serializers.CharField(write_only=True)

    class Meta:
        model = Bill
        fields = ('id', 'name', 'description', 'due_date', 'user_id', 'service_id', 'instance_service_name', 'service_name')

    def get_instance_service_name(self, obj):
        return Service.objects.get(id=obj.service_id).name

    def get_user_details(self, obj):
        user_details = {
            'id': obj.user.id,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email,
            'username': obj.user.username,
            'date_joined': obj.user.date_joined.isoformat(),
            'country': obj.user.details.country,
            'mobile_number': obj.user.details.mobile_number
        }

        return json.loads(json.dumps(user_details))

    def create(self, data):
        print('Creating a Bill with the following data: ', data)
        print('request.user: ', self.context['request'].user)

        service_name = data.get('service_name')
        service_instance = handle_service_instance(service_name)

        print('service_instance: ', service_instance)
        
        due_date = data.get('due_date')
        
        if due_date:
            if due_date > 31 or due_date < 1:
                raise ValueError('Due date must be between 1 and 31')
            else:
                pass
        
        new_bill = Bill.objects.create(
            name=data.get('name'),
            description=data.get('description'),
            due_date=due_date,
            service=service_instance,
            user=self.context['request'].user
        )

        print('New bill created: ', new_bill)
        
        return new_bill
        
    def update(self, bill_instance, data):
        print('Updating: ', bill_instance)
        print('Data: ', data)
        bill_instance.name = data.get('name')
        bill_instance.description = data.get('description')
        bill_instance.due_date = data.get('due_date')
        
        service_name = data.get('service_name')
        if service_name:
            bill_instance.service = handle_service_instance(service_name)
        
        bill_instance.save()
        
        print('Updated instance: ', bill_instance)
        return bill_instance



class ServiceSerializer(serializers.ModelSerializer):
    bills = BillSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ('id', 'name', 'bills')


class BillDetailSerializer(BillSerializer):
    payments = serializers.SerializerMethodField()
    total_bill_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = (
            'id', 'name', 'description', 'due_date', 'payments', 'user_id', 'service_id', 
            'instance_service_name', 'service_name', 'total_bill_info'
        )

    def get_payments(self, obj):
        payments_queryset = Payment.objects.filter(bill=obj, user=obj.user).order_by('due_date')
        return PaymentSerializer(payments_queryset, many=True, read_only=True).data

    def get_total_bill_info(self, obj):
        payments = Payment.objects.filter(bill=obj)
        lifetime_payment = payments.aggregate(Sum('amount'))
        payments_this_year = payments.filter(date_paid__year=TODAY.year).aggregate(Sum('amount'))
        
        return {
            'lifetime_payment': lifetime_payment.get('amount__sum'),
            'payments_this_year': payments_this_year.get('amount__sum')
        }
        
