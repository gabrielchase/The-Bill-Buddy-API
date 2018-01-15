from rest_framework import permissions

from bills.models import Bill

import requests


class BillPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # If posting to /api/bills/, request headers must contain JWT
        # If getting /api/bills/ return false
            # If getting /api/bills/:id
                # Only allow if obj.user == request.user

        if request.method == 'POST' and request.META.get('HTTP_AUTHORIZATION').split()[1]:
            return True        
        elif request.method == 'GET':
            if 'pk' in view.kwargs and view.kwargs['pk']:
                pk = view.kwargs['pk']
                obj = Bill.objects.get(id=pk)
                return obj.user == request.user
            else:
                return False
