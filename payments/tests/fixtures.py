from mixer.backend.django import mixer

from payments.models import Payment
from bills.models import Bill
from bills.tests.fixtures import new_bill

from random import randint
import pytest

@pytest.fixture
def new_payment_info():
    return {
        'amount': str(round(mixer.faker.positive_decimal(), 2)),
        'due_date': mixer.faker.date(),
        'date_paid': mixer.faker.date(),
        'status': get_status(),
        'additional_notes': mixer.faker.text(),
    }

@pytest.fixture
def new_payment():
    new_bill_instance = new_bill()
    return Payment.objects.create(
        amount=mixer.faker.positive_decimal(),
        due_date=mixer.faker.date(),
        date_paid=mixer.faker.date(),
        status=get_status(),
        additional_notes=mixer.faker.text(),
        bill=new_bill_instance,
        user=new_bill_instance.user
    )

def get_status():
    val = randint(0, 1)
    if val:
        return 'Paid'
    else:
        return 'Not Paid'