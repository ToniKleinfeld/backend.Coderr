from rest_framework import status
from rest_framework.response import Response
from offers_app.models import Offer
from reviews_app.models import Review
from rest_framework.views import APIView
from django.db.models import Avg
from django.contrib.auth import get_user_model


User = get_user_model()


class base_infoView(APIView):
    """
    View to get base information.
    """

    def get(self, request, *args, **kwargs):
        business_profile_count = User.objects.filter(type="business")
        offer_count = Offer.objects.all()
        review_count = Review.objects.all()
        rating_data = Review.objects.aggregate(avg_rating=Avg("rating"))
        average_rating = rating_data["avg_rating"]

        data = {
            "review_count": review_count.count(),
            "average_rating": round(average_rating, 2) if average_rating else 0,
            "business_profile_count": business_profile_count.count(),
            "offer_count": offer_count.count(),
        }
        return Response(data, status=status.HTTP_200_OK)
