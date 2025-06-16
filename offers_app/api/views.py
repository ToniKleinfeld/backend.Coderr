from rest_framework import viewsets, status, permissions
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from rest_framework import filters
from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferListSerializer
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 10


class OfferFilter(FilterSet):
    creator_id = NumberFilter(field_name="user", lookup_expr="exact")
    max_delivery_time = NumberFilter(field_name="min_delivery_time", lookup_expr="lte")

    class Meta:
        model = Offer
        fields = ["min_price", "max_delivery_time", "creator_id"]


class OfferViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Offer.objects.all()
    serializer_class = OfferListSerializer
    pagination_class = CustomPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = OfferFilter 
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
