from django.contrib.auth import get_user_model
from mixer.backend.django import mixer

from rest_framework.test import APIRequestFactory

from users.tests.fixtures import (json_user_with_details, other_json_user)
from users.views import UserViewSet

import json
import pytest

pytestmark = pytest.mark.django_db
User = get_user_model()
factory = APIRequestFactory()
USERS_URI = 'api/users/'


class TestUsersRegister:

    def test_user_register_with_details(self, json_user_with_details, other_json_user):
        view = UserViewSet.as_view({'post': 'create'})
        request = factory.post(USERS_URI, data=json.dumps(json_user_with_details), content_type='application/json')
        response = view(request)

        json_user_first_name = json_user_with_details['first_name']
        json_user_last_name = json_user_with_details['last_name']
        json_user_email = json_user_with_details['email']
        json_user_country = json_user_with_details['details']['country']
        json_user_mobile_number = json_user_with_details['details']['mobile_number']

        assert response.status_code == 201
        assert response.data.get('id') 
        assert not response.data.get('password') 
        assert response.data.get('email') == json_user_email
        assert response.data.get('first_name') == json_user_first_name
        assert response.data.get('last_name') == json_user_last_name

        instances_count = User.objects.filter(
                        first_name=json_user_first_name, 
                        last_name=json_user_last_name).count()
        
        # Check if username is correct
        if instances_count != 1:
            assert response.data.get('username') == '{}{}-{}'.format(json_user_first_name, json_user_last_name, instances_count)
        else:
            assert response.data.get('username') == '{}{}'.format(json_user_first_name, json_user_last_name)

        assert response.data.get('details', {}).get('country') == json_user_country
        assert response.data.get('details', {}).get('mobile_number') == json_user_mobile_number

        
    def test_user_register_without_details(self, json_user_with_details):
        json_user_with_details['details']['country'] = None
        json_user_with_details['details']['mobile_number'] = None
        
        view = UserViewSet.as_view({'post': 'create'})
        request = factory.post(USERS_URI, data=json.dumps(json_user_with_details), content_type='application/json')
        response = view(request)

        assert response.status_code == 201
        assert response.data.get('id')
        assert response.data.get('details')
        assert not response.data.get('details', {}).get('country') 
        assert not response.data.get('details', {}).get('mobile_number')
        