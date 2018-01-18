from rest_framework import permissions

from bills.models import Bill

import requests


class BillPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # If JWT 
            # Post to /api/bills/
                # return True
            # Get /api/bills/ 
                # return True
            # Get /api/bills/:id
                # Only allow if obj.user == request.user

        try:
            if request.META.get('HTTP_AUTHORIZATION').split()[1]:
                if request.method == 'POST':
                    return True        
                elif request.method == 'GET':
                    if 'pk' in view.kwargs and view.kwargs['pk']:
                        pk = view.kwargs['pk']
                        obj = Bill.objects.get(id=pk)
                        return obj.user == request.user
                    else:
                        return True
        except AttributeError:
            return False
