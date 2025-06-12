from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from profiles_app.models import Profile
from .serializers import (
    ProfileSerializer,
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user profile by pk.
    Anyone can view profiles, only the profile owner can modify their profile.
    """

    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def get_object(self):
        """
        Return the profile based on pk in URL.
        Raises 404 if profile doesn't exist.
        """
        pk = self.kwargs.get("pk")
        try:
            return Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            raise NotFound("Profile with this id not found.")

    def get(self, request, *args, **kwargs):
        """
        Retrieve a user's profile.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        Partially update a user's profile.
        Only the profile owner can update their profile.
        """
        instance = self.get_object()

        if instance.user != request.user:
            return Response(
                {"error": "Authenticated user is not the owner of the profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class FilteredTypeProfileListView(generics.ListAPIView):
    """
    Base view for profile lists - shared functionality.
    Get profiles filtered by user type with optimized queries.
    Return list of profiles filtered by type.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user__type=self.user_type).select_related("user")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class BusinessProfileListView(FilteredTypeProfileListView):
    """
    List all business profiles.
    """

    serializer_class = BusinessProfileListSerializer
    user_type = "business"


class CustomerProfileListView(FilteredTypeProfileListView):
    """
    List all customer profiles.
    """

    serializer_class = CustomerProfileListSerializer
    user_type = "customer"
