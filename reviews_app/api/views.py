from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from reviews_app.models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.all()

    def list(self, request):
        """GET /api/reviews/ - Liste aller Reviews des aktuellen Users"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """GET /api/reviews/{pk}/ - Einzelnes Review"""
        review = get_object_or_404(Review, pk=pk, reviewer=request.user)
        serializer = self.get_serializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """POST /api/reviews/ - Neues Review erstellen"""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Zusätzliche Überprüfung für 403 Status
            business_user_id = serializer.validated_data.get("business_user")
            if Review.objects.filter(
                business_user_id=business_user_id, reviewer=request.user
            ).exists():
                return Response(
                    {
                        "detail": "Sie haben bereits ein Review für diesen Business User erstellt."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            review = serializer.save()
            response_serializer = self.get_serializer(review)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """PATCH /api/reviews/{pk}/ - Review teilweise aktualisieren"""
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response(
                {"detail": "Review nicht gefunden."}, status=status.HTTP_404_NOT_FOUND
            )

        # Überprüfe ob aktueller User der reviewer ist
        if review.reviewer != request.user:
            return Response(
                {
                    "detail": "Der Benutzer ist nicht berechtigt, diese Bewertung zu bearbeiten."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(review, data=request.data, partial=True)

        if serializer.is_valid():
            updated_review = serializer.save()
            response_serializer = self.get_serializer(updated_review)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """DELETE /api/reviews/{pk}/ - Review löschen"""
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response(
                {"detail": "Review nicht gefunden."}, status=status.HTTP_404_NOT_FOUND
            )

        # Überprüfe ob aktueller User der reviewer ist
        if review.reviewer != request.user:
            return Response(
                {
                    "detail": "Der Benutzer ist nicht berechtigt, diese Bewertung zu löschen."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        review.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

#TODO: durchgehen und überprüfen ob alles sin macht , weiter müssen noch filter querys mit