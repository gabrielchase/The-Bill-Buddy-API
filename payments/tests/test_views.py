from rest_framework.test import APIRequestFactory

from payments.models import Payment
from payments.tests.fixtures import new_payment_info
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
