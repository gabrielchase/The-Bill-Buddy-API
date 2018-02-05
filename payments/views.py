from rest_framework import (generics, viewsets)
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from bills.models import Bill

from payments.models import Payment 
from payments.permissions import PaymentPermission
from payments.serializers import PaymentSerializer

from datetime import datetime
NOW = datetime.now()


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (PaymentPermission,)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise ValueError('JWT not found in request headers')

        return Payment.objects.filter(user=self.request.user)
        

class CreateMultiplePayments(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (PaymentPermission,)

    def create(self, request):
        bill_id = request.data.get('bill_id')
        bill = Bill.objects.get(id=bill_id)
        months = request.data.get('months')
        days = request.data.get('days')

        print('Creating multiple payments for {}'.format(bill.name))
        print('Months: ', months)
        print('Days: ', days)

        try: 
            for month in months:
                due_date_string = ''
                for day in days: 
                    due_date_string = '{} {} {}'.format(month, day, NOW.year)
                    due_date_datetime = datetime.strptime(due_date_string, '%B %d %Y')

                    Payment.objects.create(
                        amount=0, 
                        due_date=due_date_datetime,
                        date_paid=None,
                        status='Not Paid',
                        additional_notes=None,
                        bill=bill,
                        user=request.user
                    )

            print('Successfully created all payments')
            return Response({'status': 'created'}, status=status.HTTP_201_CREATED)
        except: 
            print('Unsuccessfully created payments')
            return Response({'error': 'Error'}, status=status.HTTP_400_BAD_REQUEST)
