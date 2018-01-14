from django.contrib.auth import get_user_model

from rest_framework import serializers

from users.models import Details

User = get_user_model()


class DetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Details
        fields = ('country', 'mobile_number')


class UserSerializer(serializers.ModelSerializer):
    details = DetailsSerializer()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'last_login', 'date_joined', 'password',
            'details'
        )
        read_only_fields = ('username', 'last_login', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, data):
        details = data.pop('details')
        new_user = User.objects.create_user(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            country=details.get('country'),
            mobile_number=details.get('mobile_number'),
            password=data.get('password')
        )

        return new_user