from django.contrib.auth import get_user_model

from rest_framework import serializers

from bills.models import (Bill, Service)

from users.serializers import (UserSerializer)

User = get_user_model()


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ('id', 'name',)


class BillSerializer(serializers.ModelSerializer):

    user_details = serializers.SerializerMethodField()
    service = ServiceSerializer()

    class Meta:
        model = Bill
        fields = ('id', 'name', 'description', 'due_date', 'service', 'user_details')

    def get_user_details(self, obj):
        user_details = {
            'id': obj.user.id,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email,
            'username': obj.user.username,
            'date_joined': obj.user.date_joined.isoformat(),
            'country': obj.user.details.country,
            'mobile_number': obj.user.details.goal
        }

        return json.loads(json.dumps(user_details))

    # def create(self, data):
    #     name = data.get()
    #     if due_date:
    #         if due_date > 31 or due_date < 1:
    #             raise ValueError('Due date must be between 1 and 31')
    #         else:
    #             pass

    #     service_instance = None
        
    #     try:
    #         service_instance = Service.objects.get(name=service)
    #     except Service.DoesNotExist:
    #         service_instance = Service.create_service(name=service)
        
    #     new_bill = self.model(
    #         name=name,
    #         description=description,
    #         due_date=due_date,
    #         service=service_instance,
    #         user=user
    #     )
    #     new_bill.save()
        
    #     return new_bill