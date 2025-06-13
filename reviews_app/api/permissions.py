from rest_framework import permissions


class ReviewPermission(permissions.IsAuthenticated):
    """
    Custom Permission for Review (extends IsAuthenticated):
    - POST: User must have type 'customer'
    - PATCH: User must be the reviewer of the review and have type 'customer'
    - DELETE: User must be the reviewer of the review and have type 'customer'
    - GET: All authenticated users
    """

    def has_permission(self, request, view):
        """
        Checks if the user is generally authorized
        """

        if not super().has_permission(request, view):
            return False
        
        if request.method == 'POST':
            if not hasattr(request.user, 'type') or request.user.type != 'customer':
                return False
        
        return True

    def has_object_permission(self, request, view, obj):
        """
        Checks if the user is authorized to access the specific review object
        """

        if request.method in ['PATCH', 'DELETE']:
            return obj.reviewer == request.user
        
        return True