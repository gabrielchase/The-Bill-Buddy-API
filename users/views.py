from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework import viewsets
from rest_framework import status
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from users.permissions import UserPermission
from users.serializers import (UserSerializer, UserLoginSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (UserPermission,)


class LoginAPIView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = get_object_or_404(User, email=email)
        
        if user.check_password(password):
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            
            user.last_login = timezone.now()
            user.save()
            
            return Response({
                'user_id': user.id,
                'email': user.email,
                'token': token
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Error in verifying user'}, status=status.HTTP_400_BAD_REQUEST)
