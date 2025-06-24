from rest_framework import permissions


class OffersPermission(permissions.IsAuthenticated):
    """
    Custom Permission for Offers:
    - LIST: No authentication required
    - POST: User must be authenticated and have type 'business'
    - RETRIEVE/PATCH/DELETE: User must be authenticated
    - PATCH/DELETE: User must be the offer.user of the offer and have type 'business'
    """

    def has_permission(self, request, view):
        """
        Checks if the user is generally authorized
        """
        if view.action == "list":
            return True

        if not super().has_permission(request, view):
            return False

        if request.method == "POST":
            if not hasattr(request.user, "type") or request.user.type != "business":
                return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        Checks if the user is authorized to access the specific review object
        """

        if request.method in ["PATCH", "DELETE"]:
            return obj.user == request.user

        return True