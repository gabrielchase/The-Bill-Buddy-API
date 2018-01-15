from django.contrib.auth import get_user_model

from mixer.backend.django import mixer

from bills.models import (Bill, Service)
from bills.tests.fixtures import (new_user, new_bill, new_bill_info)
from bills.utils import handle_service_instance

# IMPORTANT: Allows tests to write into the database 
import pytest
pytestmark = pytest.mark.django_db
User = get_user_model()


class TestBillsModels:

    def test_model_create_bill(self, new_user, new_bill_info):
        new_bill_instance = Bill.objects.create(
            name=new_bill_info['name'],
            description=new_bill_info['description'],
            due_date=new_bill_info['due_date'],
            service=handle_service_instance(new_bill_info['service_name']),
            user=new_user
        )

        assert new_bill_instance.id
        assert new_bill_instance.name == new_bill_info['name']
        assert new_bill_instance.description == new_bill_info['description']
        assert new_bill_instance.due_date == new_bill_info['due_date']
        assert Service.objects.get(name=new_bill_info['service_name'].title()).id
        assert new_bill_instance.user == new_user
        