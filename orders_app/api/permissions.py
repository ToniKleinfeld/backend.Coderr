from rest_framework import permissions


class OrdersPermissions(permissions.IsAuthenticated):
    """
    Custom Permission for Order:
    - GET: authentication required
    - POST: User must be authenticated and have type 'customer'
    - PATCH: User must be the order.business_user of the order
    - DELETE: User must be staff or admin
    """

    def has_permission(self, request, view):
        """
        Checks if the user is generally authorized
        """

        if not super().has_permission(request, view):
            return False

        if request.method == "POST":
            if not hasattr(request.user, "type") or request.user.type != "customer":
                return False

        if request.method == "DELETE":
            if not (request.user.is_staff or request.user.is_superuser):
                return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        Checks if the user is authorized to access the specific review object
        Only the business_user can PATCH their order
        """

        if request.method in ["PATCH"]:
            return obj.business_user == request.user

        return True
