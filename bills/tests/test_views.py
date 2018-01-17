from django.contrib.auth import get_user_model
from mixer.backend.django import mixer

from rest_framework.test import APIRequestFactory

from bills.tests.fixtures import (new_bill_info, new_bill)
from bills.views import BillViewSet

from users.tests.fixtures import new_user
from users.tests.utils import get_jwt_header

import json
import pytest

pytestmark = pytest.mark.django_db
User = get_user_model()
factory = APIRequestFactory()
BILLS_URI = 'api/bills/'


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
        
        assert response.data.get('service', {}).get('id')
        assert response.data.get('service', {}).get('name') == new_bill_info['service']['name'].title()

        assert response.data.get('user_details', {}).get('id') == new_user.id
        assert response.data.get('user_details', {}).get('email') == new_user.email
        assert response.data.get('user_details', {}).get('username') == new_user.username
        assert response.data.get('user_details', {}).get('first_name') == new_user.first_name
        assert response.data.get('user_details', {}).get('last_name') == new_user.last_name







