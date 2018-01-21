from payments.models import Payment
from payments.tests.fixtures import new_payment

import pytest
pytestmark = pytest.mark.django_db


class TestPaymentModels:

    def test_model_create_payment(self, new_payment):
        assert new_payment.id
        assert Payment.objects.get(id=new_payment.id)
        assert new_payment.amount
        assert new_payment.due_date
        assert new_payment.date_paid
        assert new_payment.due_date
        assert new_payment.status
        assert new_payment.bill 
        assert new_payment.user
        assert new_payment.bill.user == new_payment.user
        assert str(new_payment) == '{}: {}'.format(new_payment.bill, new_payment.id)
        