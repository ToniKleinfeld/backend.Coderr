from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django_filters import rest_framework as django_filters_rest

from rest_framework import filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from reviews_app.models import Review
from reviews_app.api.permissions import ReviewPermission
from reviews_app.api.serializers import ReviewSerializer


class ReviewModelFilterSet(django_filters.FilterSet):
    """
    Custom filter set for Review model.
    Allows filtering by business_user_id and reviewer_id.
    """

    business_user_id = django_filters.NumberFilter(field_name="business_user__id")
    reviewer_id = django_filters.NumberFilter(field_name="reviewer__id")

    class Meta:
        model = Review
        fields = ["business_user_id", "reviewer_id"]


class ReviewViewSet(viewsets.ModelViewSet):
    """
    POST: Create a new Review from current User
    PATCH: Updates an existing review (rating and description only) ,reviewer = current user
    DELETE: Delete a review when reviewer = current user
    GET Detail: Deactivated, as filters are to be used
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [ReviewPermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ReviewModelFilterSet
    ordering_fields = ["rating", "updated_at"]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        business_user_id = data.get("business_user")
        if business_user_id:
            existing_review = Review.objects.filter(business_user_id=business_user_id, reviewer=request.user).first()

            if existing_review:
                return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        review = serializer.save(reviewer=request.user)

        response_serializer = self.get_serializer(review)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        allowed_fields = ["rating", "description"]
        filtered_data = {key: value for key, value in request.data.items() if key in allowed_fields}

        serializer = self.get_serializer(instance, data=filtered_data, partial=partial)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        return Response(
            {"detail": "Detail queries are not available. Use the filter options."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
