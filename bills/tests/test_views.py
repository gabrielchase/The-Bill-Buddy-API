from django.contrib.auth import get_user_model
from mixer.backend.django import mixer

from rest_framework.test import APIRequestFactory

from bills.models import (Bill, Service)
from bills.tests.fixtures import (new_bill_info, other_bill_info, new_bill, other_bill)
from bills.views import (BillViewSet, ServiceList)
from bills.utils import handle_service_instance

from users.tests.fixtures import (new_user, other_user)
from users.tests.utils import get_jwt_header

from random import randint

import json
import pytest
import requests

pytestmark = pytest.mark.django_db
User = get_user_model()
factory = APIRequestFactory()
BILLS_URI = 'api/bills/'
SERVICES_URI = 'api/services/'


class TestBillsViews: 

    def test_bill_post(self, new_bill_info, new_user):
        view = BillViewSet.as_view({'post': 'create'})
        request = factory.post(
            BILLS_URI, 
            data=json.dumps(new_bill_info), 
            HTTP_AUTHORIZATION=get_jwt_header(new_user.email),
            content_type='application/json'
        )
        response = view(request)

        assert response.status_code == 201
        
        assert response.data.get('id')
        assert response.data.get('name') == new_bill_info['name']
        assert response.data.get('description') == new_bill_info['description']
        assert response.data.get('due_date') == new_bill_info['due_date']
        assert response.data.get('service_id') 
        assert Service.objects.get(id=response.data.get('service_id'))
        assert response.data.get('user_id') == new_user.id

        # assert response.data.get('user_details', {}).get('id') == new_user.id
        # assert response.data.get('user_details', {}).get('email') == new_user.email
        # assert response.data.get('user_details', {}).get('username') == new_user.username
        # assert response.data.get('user_details', {}).get('first_name') == new_user.first_name
        # assert response.data.get('user_details', {}).get('last_name') == new_user.last_name

    def test_get_bills_list(self, new_user, other_user): 
        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance(mixer.faker.genre()),
            user=new_user
        )
        
        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance(mixer.faker.genre()),
            user=new_user
        )

        good_list_view = BillViewSet.as_view({'get': 'list'})
        good_list_request = factory.get(
            BILLS_URI, 
            HTTP_AUTHORIZATION=get_jwt_header(new_user.email),
        )
        good_list_response = good_list_view(good_list_request)
        
        assert good_list_response.status_code == 200
        
        bills = good_list_response.data
        assert len(bills) == 2
        
        for bill in bills:
            assert bill.get('id')
            assert bill.get('name')
            assert bill.get('description')
            assert bill.get('due_date')
            assert bill.get('service_id')
            assert bill.get('user_id') == new_user.id
        
    def test_retrieve_bill(self, new_bill, other_user):
        view = BillViewSet.as_view({'get': 'retrieve'})
        good_request = factory.get(
            BILLS_URI,
            HTTP_AUTHORIZATION=get_jwt_header(new_bill.user.email),
        )
        good_response = view(good_request, pk=new_bill.id)
        
        assert good_response.status_code == 200
        assert good_response.data.get('id') == new_bill.id
        assert good_response.data.get('name') == new_bill.name
        assert good_response.data.get('description') == new_bill.description
        assert good_response.data.get('due_date') == new_bill.due_date
        assert good_response.data.get('service_id') == new_bill.service.id
        assert good_response.data.get('user_id') == new_bill.user.id
        assert isinstance(good_response.data.get('payments'), list)

    def test_get_bills_and_query_by_service(self, new_user):
        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance('House'),
            user=new_user
        )
        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance('House'),
            user=new_user
        )
        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance('House'),
            user=new_user
        )
        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance('Membership'),
            user=new_user
        )
        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance('Membership'),
            user=new_user
        )

        view = BillViewSet.as_view({'get': 'list'})
        Bill.objects.count() == 5
        membership_request = factory.get(
            BILLS_URI + '?service=Membership',
            HTTP_AUTHORIZATION=get_jwt_header(new_user.email),
        )
        membership_response = view(membership_request)
        
        assert membership_response.status_code == 200
        assert len(membership_response.data) == 2
        for bill in membership_response.data:
            assert bill.get('id')
            assert bill.get('service_id')
            assert bill.get('user_id') == new_user.id

        house_request = factory.get(
            BILLS_URI + '?service=House',
            HTTP_AUTHORIZATION=get_jwt_header(new_user.email),
        )
        house_response = view(house_request)
        
        assert house_response.status_code == 200
        assert len(house_response.data) == 3
        for bill in house_response.data:
            assert bill.get('id')
            assert bill.get('service_id')
            assert bill.get('user_id') == new_user.id

    def test_get_other_bills_should_be_forbidden(self, new_user, other_user):
        b1 = Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance(mixer.faker.genre()),
            user=new_user
        )

        assert b1.id
        assert b1.user == new_user

        bad_retrieve_view = BillViewSet.as_view({'get': 'retrieve'})
        bad_retrieve_request = factory.get(
            BILLS_URI,
            HTTP_AUTHORIZATION=get_jwt_header(other_user.email),
        )
        bad_retrieve_response = bad_retrieve_view(bad_retrieve_request, pk=b1.id)
        
        assert bad_retrieve_response.status_code == 403

    def test_bill_update_by_good_user(self, new_user, other_bill_info):
        b1 = Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance(mixer.faker.genre()),
            user=new_user
        )

        assert b1.id
        assert b1.user == new_user        

        view = BillViewSet.as_view({'put': 'update'})
        request = factory.put(
            BILLS_URI,
            data=json.dumps(other_bill_info), 
            content_type='application/json',
            HTTP_AUTHORIZATION=get_jwt_header(new_user.email)
        )
        response = view(request, pk=b1.id)
        print(response.data)
        assert response.status_code == 200
        assert response.data.get('id') == b1.id
        assert response.data.get('name') == other_bill_info['name']
        assert response.data.get('description') == other_bill_info['description']
        assert response.data.get('due_date') == other_bill_info['due_date']
        service_id = response.data.get('service_id') 
        assert service_id
        assert Service.objects.get(id=service_id)

    def test_bill_update_by_bad_user(self, new_bill_info, other_bill_info, new_user, other_user):
        new_bill_instance = Bill.objects.create(
            name=new_bill_info['name'],
            description=new_bill_info['description'],
            due_date=new_bill_info['due_date'],
            service=handle_service_instance(new_bill_info['service_name']),
            user=new_user
        )

        assert new_bill_instance.id

        view = BillViewSet.as_view({'put': 'update'})
        request = factory.put(
            BILLS_URI,
            data=json.dumps(other_bill_info), 
            content_type='application/json',
            HTTP_AUTHORIZATION=get_jwt_header(other_user.email)
        )
        response = view(request, pk=new_bill_instance.id)

        assert response.status_code == 403
        

class TestServicesView:

    def test_service_get_list(self, new_user):
        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance('House'),
            user=new_user
        )

        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance('House'),
            user=new_user
        )

        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance('Medical'),
            user=new_user
        )

        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance('Medical'),
            user=new_user
        )

        Bill.objects.create(
            name=mixer.faker.first_name(),
            description=mixer.faker.text(),
            due_date=randint(1, 31),
            service=handle_service_instance('Medical'),
            user=new_user
        )

        view = ServiceList.as_view()
        request = factory.get(
            SERVICES_URI,
            content_type='application/json',
            HTTP_AUTHORIZATION=get_jwt_header(new_user.email)
        )
        response = view(request)

        assert response.status_code == 200
        assert len(response.data) == 2
        
        for service in response.data:
            assert service.get('id')
            
            if service.get('name') == 'Medical':
                assert len(service.get('bills')) == 3
            elif service.get('name') == 'House':
                assert len(service.get('bills')) == 2
            
            for bill in service.get('bills'):
                assert bill.get('id')
                assert bill.get('name')
                assert bill.get('description')
                assert bill.get('due_date')
                assert bill.get('service_id') == service.get('id')
                assert bill.get('user_id') == new_user.id
                