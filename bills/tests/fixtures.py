from mixer.backend.django import mixer
from django.contrib.auth import get_user_model

from bills.models import Bill
from bills.utils import handle_service_instance

from users.tests.fixtures import new_user

from random import randint

import pytest

User = get_user_model()

@pytest.fixture
def new_bill_info():
    return {
        'name': mixer.faker.genre(),
        'description': mixer.faker.text(),
        'due_date': randint(1, 31),
        'service': {
            'name': mixer.faker.genre()
        }
    }

@pytest.fixture
def new_bill(new_user):
    return Bill.objects.create(
        name=mixer.faker.first_name(),
        description=mixer.faker.text(),
        due_date=randint(1, 31),
        service=handle_service_instance(mixer.faker.genre()),
        user=new_user
    )