from django.contrib.auth import get_user_model
from mixer.backend.django import mixer

from rest_framework.test import APIRequestFactory

from users.tests.fixtures import (
    json_user_with_details, other_json_user_with_details, new_user, other_user)
from users.tests.utils import get_jwt_header
from users.views import (UserViewSet, LoginAPIView)

import json
import pytest

pytestmark = pytest.mark.django_db
User = get_user_model()
factory = APIRequestFactory()

USERS_URI = 'api/users/'
LOGIN_URI = 'api/login/'


class TestUsersViews:

    def test_user_register_with_details(self, json_user_with_details):
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
        assert response.data.get('username') == '{}{}-{}'.format(json_user_first_name, json_user_last_name, response.data.get('id'))
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
        assert response.data.get('details', {}).get('user_id') == response.data.get('id')
        assert not response.data.get('details', {}).get('country') 
        assert not response.data.get('details', {}).get('mobile_number')
        
    def test_user_get_all_users(self, new_user):
        user_list_view = UserViewSet.as_view({'get': 'list'})
        
        unauthenticated_request = factory.get(USERS_URI)
        unauthenticated_response = user_list_view(unauthenticated_request)
        assert unauthenticated_response.status_code == 401 

        authenticated_request = factory.get(
            USERS_URI, 
            HTTP_AUTHORIZATION=get_jwt_header(new_user.email)
        )
        authenticated_response = user_list_view(unauthenticated_request)
        assert authenticated_response.status_code == 401

    def test_user_get_self(self, new_user):
        view = UserViewSet.as_view({'get': 'retrieve'})
        request = factory.get(
            USERS_URI,
            HTTP_AUTHORIZATION=get_jwt_header(new_user.email) 
        )
        response = view(request, pk=new_user.id)

        assert response.status_code == 200
        assert response.data.get('id') == new_user.id
        assert response.data.get('email') == new_user.email
        assert response.data.get('username') == new_user.username

    def test_user_get_other_user(self, new_user, other_user):
        view = UserViewSet.as_view({'get': 'retrieve'})
        request = factory.get(
            USERS_URI,
            HTTP_AUTHORIZATION=get_jwt_header(new_user.email) 
        )
        response = view(request, pk=other_user.id)

        assert response.status_code == 403
    
    def test_user_update_self(self, json_user_with_details, other_json_user_with_details):
        user = User.objects.create_user(
            first_name=json_user_with_details['first_name'],
            last_name=json_user_with_details['last_name'],
            email=json_user_with_details['email'],
            country=json_user_with_details['details']['country'],
            mobile_number=json_user_with_details['details']['mobile_number'],
            password=json_user_with_details['password']
        )

        assert user.id
        assert user.email == json_user_with_details['email']
        assert user.username == '{}{}-{}'.format(json_user_with_details['first_name'], json_user_with_details['last_name'], user.id)

        other_json_user_with_details['password'] = json_user_with_details['password']
        
        view = UserViewSet.as_view({'put': 'update'})
        request = factory.put(
            USERS_URI,
            data=json.dumps(other_json_user_with_details), 
            content_type='application/json',
            HTTP_AUTHORIZATION=get_jwt_header(user.email)
        )
        response = view(request, pk=user.id)

        assert response.status_code == 200
        assert response.data.get('id') == user.id
        assert User.objects.get(id=response.data.get('id')) == User.objects.get(id=user.id)
        assert response.data.get('first_name') == other_json_user_with_details['first_name']
        assert response.data.get('last_name') == other_json_user_with_details['last_name']
        assert response.data.get('email') == other_json_user_with_details['email']
        assert response.data.get('username') == '{}{}-{}'.format(other_json_user_with_details['first_name'], other_json_user_with_details['last_name'], response.data.get('id'))
        assert response.data.get('details', {}).get('country') == other_json_user_with_details['details']['country']
        assert response.data.get('details', {}).get('mobile_number') == other_json_user_with_details['details']['mobile_number']
        

class TestUsersLogin:

    def test_jwt_return_on_login(self, json_user_with_details):
        register_view = UserViewSet.as_view({'post': 'create'})
        register_request = factory.post(USERS_URI, data=json.dumps(json_user_with_details), content_type='application/json')
        register_response = register_view(register_request)

        assert register_response.status_code == 201
        assert register_response.data.get('id')

        login_view =  LoginAPIView.as_view()
        login_data = {'email': json_user_with_details['email'], 'password': json_user_with_details['password']}
        login_request = factory.post(LOGIN_URI, data=json.dumps(json_user_with_details), content_type='application/json')
        login_response = login_view(login_request)

        assert login_response.status_code == 200
        assert login_response.data.get('user_id') == register_response.data.get('id')
        assert login_response.data.get('email') == register_response.data.get('email')
        assert login_response.data.get('token')
