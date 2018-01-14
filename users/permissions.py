from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        # Allow user registration
        if request.method == 'POST':
            return True
        
        # Don't allow users to get list of all users
        # REFACTOR when groups and permissions are added
            # Only allow admin to see all users
        return view.kwargs.get('pk', False)

    def has_object_permission(self, request, view, obj):
        
        # If the object being viewed is the same as the request user
        # Allow user to GET, PUT, DELETE
        if request.method in permissions.SAFE_METHODS + ('PUT', 'DELETE'):
            return obj == request.user