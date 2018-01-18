from django.contrib.auth import get_user_model

from rest_framework import serializers

from bills.models import (Bill, Service)

from users.models import Details

User = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)


class DetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Details
        fields = ('user_id', 'country', 'mobile_number')


class UserSerializer(serializers.ModelSerializer):
    details = DetailsSerializer()
    services = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'last_login', 'date_joined', 'password',
            'details', 'services'
        )
        read_only_fields = ('username', 'last_login', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_services(self, obj):
        service_ids = Bill.objects.filter(user=obj).values('service_id').distinct()
        service_names = []
        for obj in service_ids:
            service = Service.objects.get(id=obj['service_id'])
            service_names.append(service.name)

        return service_names

    def create(self, data):
        print('Creating user with data: ', data)
        details = data.pop('details')
        new_user = User.objects.create_user(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            country=details.get('country'),
            mobile_number=details.get('mobile_number'),
            password=data.get('password')
        )
        print('Created new user for {}'.format(new_user))
        return new_user

    def update(self, user_instance, data):
        password = data.get('password')
        details = data.get('details')
        
        if user_instance.check_password(password):
            user_instance.first_name = data.get('first_name')
            user_instance.last_name = data.get('last_name')
            user_instance.email = data.get('email')
            user_instance.save()
            user_instance.set_username()

            if details:
                detail_instance = Details.objects.get(user_id=user_instance.id)
                detail_instance.country = details.get('country')
                detail_instance.mobile_number = details.get('mobile_number')
                detail_instance.save()

        return user_instance
