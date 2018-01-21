from mixer.backend.django import mixer

from rest_framework.test import APIRequestFactory

from payments.models import Payment
from payments.tests.fixtures import (new_payment, other_payment, new_payment_info, get_status)
from payments.views import PaymentViewSet

from bills.tests.fixtures import new_bill

from users.tests.fixtures import other_user 
from users.tests.utils import get_jwt_header

import json
import pytest

factory = APIRequestFactory()
pytestmark = pytest.mark.django_db
PAYMENTS_URI = 'api/payments/'


class TestPaymentsViews:

    def test_payment_create(self, new_payment_info, new_bill):
        new_payment_info['bill_id'] = new_bill.id
        view = PaymentViewSet.as_view({'post': 'create'})
        request = factory.post(
            PAYMENTS_URI,
            data=json.dumps(new_payment_info),
            content_type='application/json',
            HTTP_AUTHORIZATION=get_jwt_header(new_bill.user.email)
        )
        response = view(request)

        assert response.status_code == 201
        assert response.data.get('id')
        assert response.data.get('amount') == new_payment_info['amount']
        assert response.data.get('due_date') == new_payment_info['due_date']
        assert response.data.get('date_paid') == new_payment_info['date_paid']
        assert response.data.get('status') == new_payment_info['status']
        assert response.data.get('additional_notes') == new_payment_info['additional_notes']
        assert response.data.get('bill_id') == new_bill.id
        assert response.data.get('user_id') == new_bill.user.id

        payment_instance = Payment.objects.get(id=response.data.get('id'))
        
        assert payment_instance.bill == new_bill
        assert payment_instance.user == new_bill.user

    def test_payment_list(self, new_bill):
        Payment.objects.create(
            amount=mixer.faker.positive_decimal(),
            due_date=mixer.faker.date(),
            date_paid=mixer.faker.date(),
            status=get_status(),
            additional_notes=mixer.faker.text(),
            bill=new_bill,
            user=new_bill.user
        )

        Payment.objects.create(
            amount=mixer.faker.positive_decimal(),
            due_date=mixer.faker.date(),
            date_paid=mixer.faker.date(),
            status=get_status(),
            additional_notes=mixer.faker.text(),
            bill=new_bill,
            user=new_bill.user
        )

        Payment.objects.create(
            amount=mixer.faker.positive_decimal(),
            due_date=mixer.faker.date(),
            date_paid=mixer.faker.date(),
            status=get_status(),
            additional_notes=mixer.faker.text(),
            bill=new_bill,
            user=new_bill.user
        )

        view = PaymentViewSet.as_view({'get': 'list'})
        request = factory.get(
            PAYMENTS_URI,
            HTTP_AUTHORIZATION=get_jwt_header(new_bill.user.email)
        )
        response = view(request)

        assert response.status_code == 200
        assert len(response.data) == 3
        for payment in response.data:
            assert payment.get('id')
            assert payment.get('bill_id') == new_bill.id
            assert payment.get('user_id') == new_bill.user.id 

    def test_retrieve_good(self, new_payment):
        view = PaymentViewSet.as_view({'get': 'retrieve'})
        request = factory.get(
            PAYMENTS_URI,
            HTTP_AUTHORIZATION=get_jwt_header(new_payment.user.email)
        )
        response = view(request, pk=new_payment.id)

        assert response.status_code == 200
        assert response.data.get('id') == new_payment.id
        assert response.data.get('amount') == str(round(new_payment.amount, 2))
        assert response.data.get('due_date') == new_payment.due_date
        assert response.data.get('date_paid') == new_payment.date_paid
        assert response.data.get('status') == new_payment.status
        assert response.data.get('additional_notes') == new_payment.additional_notes
        assert response.data.get('bill_id') == new_payment.bill.id
        assert response.data.get('user_id') == new_payment.bill.user.id 

    def test_retrieve_bad(self, new_payment, other_user):
        view = PaymentViewSet.as_view({'get': 'retrieve'})
        request = factory.get(
            PAYMENTS_URI,
            HTTP_AUTHORIZATION=get_jwt_header(other_user.email)
        )
        response = view(request, pk=new_payment.id)

        assert response.status_code == 403

    def test_payment_update_good(self, new_payment, new_payment_info):
        view = PaymentViewSet.as_view({'put': 'update'})
        request = factory.put(
            PAYMENTS_URI,
            data=json.dumps(new_payment_info),
            content_type='application/json',
            HTTP_AUTHORIZATION=get_jwt_header(new_payment.user.email)
        )
        response = view(request, pk=new_payment.id)

        assert response.status_code == 200
        assert response.data.get('id') == new_payment.id
        assert response.data.get('bill_id') == new_payment.bill.id
        assert response.data.get('user_id') == new_payment.user.id

        assert response.data.get('amount') == new_payment_info['amount']
        assert response.data.get('due_date') == new_payment_info['due_date']
        assert response.data.get('date_paid') == new_payment_info['date_paid']
        assert response.data.get('status') == new_payment_info['status']
        assert response.data.get('additional_notes') == new_payment_info['additional_notes']

    def test_payment_update_bad(self, new_payment, new_payment_info, other_user):
        view = PaymentViewSet.as_view({'put': 'update'})
        request = factory.put(
            PAYMENTS_URI,
            data=json.dumps(new_payment_info),
            content_type='application/json',
            HTTP_AUTHORIZATION=get_jwt_header(other_user.email)
        )
        response = view(request, pk=new_payment.id)
        
        assert response.status_code == 403
        