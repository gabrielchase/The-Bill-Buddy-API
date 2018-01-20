from rest_framework import permissions

from payments.models import Payment


class PaymentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # If JWT 
            # Post, Put, Delete to /api/bills/
                # return True
            # Get /api/bills/ 
                # return True
            # Get /api/bills/:id
                # Only allow if obj.user == request.user

        try:
            if request.META.get('HTTP_AUTHORIZATION').split()[1]:
                if request.method in 'POST':
                    return True
                elif request.method in ['GET', 'PUT', 'DELETE']:
                    if 'pk' in view.kwargs and view.kwargs['pk']:
                        # /api/bills/:id/
                        pk = view.kwargs['pk']
                        obj = Payment.objects.get(id=pk)
                        return obj.user == request.user
                    else:
                        # /api/bills/
                        return True
        except AttributeError:
            return False
