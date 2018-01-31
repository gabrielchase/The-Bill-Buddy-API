from django.contrib.auth import get_user_model

from rest_framework import (serializers, status)
from rest_framework.response import Response

from bills.models import (Bill, Service)

from payments.models import Payment

from users.models import Details

import datetime

User = get_user_model()
TODAY = datetime.date.today()


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)


class DetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Details
        fields = ('user_id', 'country', 'mobile_number')


class UserSerializer(serializers.ModelSerializer):
    details = DetailsSerializer()
    services = serializers.SerializerMethodField()
    payments_this_month = serializers.SerializerMethodField()
    expenditure_this_year = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'last_login', 'date_joined', 'password',
            'details', 'services', 'payments_this_month', 'expenditure_this_year'
        )
        read_only_fields = ('username', 'last_login', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_services(self, obj):
        service_ids = Bill.objects.filter(user=obj).values('service_id').distinct()
        service_names = []
        for obj in service_ids:
            service = Service.objects.get(id=obj['service_id'])
            service_names.append(service.name)

        return service_names
    
    def get_payments_this_month(self, user_instance):
        payments_this_month = []
        user_payments = Payment.objects.filter(
            user=user_instance, 
            due_date__year=TODAY.year, # not required but more explicit
            due_date__month=TODAY.month
        ).order_by('due_date')
        for payment in user_payments:
            payment_dict = {
                'amount': payment.amount,
                'due_date': payment.due_date,
                'status': payment.status,
                'additional_notes': payment.additional_notes, 
                'bill_name': payment.bill.name,
                'service': payment.bill.service.name
            }
            payments_this_month.append(payment_dict)
        print('{} payments this month: '.format(user_instance.email), payments_this_month)
        return payments_this_month

    def get_expenditure_this_year(self, user_instance):
        expenditure_this_year = { 'total': 0 }
        payments = Payment.objects.filter(
            user=user_instance, 
            date_paid__year=TODAY.year, # not required but more explicit
            status='Paid'
        )
        keys = []
        for payment in payments:
            expenditure_this_year['total'] += payment.amount
            bill_name_key = payment.bill.name.replace(' ', '_')
            keys.append(bill_name_key)
            expenditure_this_year.update({ bill_name_key:  payment.amount })

        for key in keys:
            bill_amount = expenditure_this_year[key]
            bill_percentage = round(bill_amount / expenditure_this_year['total'], 2)
            new_key = key + '_percentage'
            expenditure_this_year.update({ new_key: bill_percentage })

        print('{} expenditure this year: '.format(user_instance.email), expenditure_this_year)
        return expenditure_this_year


    def create(self, data):
        print('Creating user with data: ', data)
        details = data.pop('details')
        new_user = User.objects.create_user(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            country=details.get('country'),
            mobile_number=details.get('mobile_number'),
            password=data.get('password')
        )
        print('Created new user for {}'.format(new_user))
        return new_user

    def update(self, user_instance, data):
        password = data.get('password')
        details = data.get('details')
        
        if user_instance.check_password(password):
            user_instance.first_name = data.get('first_name')
            user_instance.last_name = data.get('last_name')
            user_instance.email = data.get('email')
            user_instance.save()
            user_instance.set_username()

            if details:
                detail_instance = Details.objects.get(user_id=user_instance.id)
                detail_instance.country = details.get('country')
                detail_instance.mobile_number = details.get('mobile_number')
                detail_instance.save()

            return user_instance
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
