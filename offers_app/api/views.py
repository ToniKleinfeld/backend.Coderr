from rest_framework import viewsets, status, permissions, mixins
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from rest_framework.response import Response
from rest_framework import filters
from offers_app.models import Offer, OfferDetail
from django.db.models import Min
from offers_app.api.serializers import (
    OfferListSerializer,
    OfferCreateSerializer,
    OfferUpdateSerializer,
    OfferDetailSerializer,
)
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 10


class OfferFilter(FilterSet):
    creator_id = NumberFilter(field_name="user", lookup_expr="exact")
    max_delivery_time = NumberFilter(field_name="min_delivery_time", lookup_expr="lte")
    min_price = NumberFilter(field_name="min_price", lookup_expr="gte")

    class Meta:
        model = Offer
        fields = ["min_price", "max_delivery_time", "creator_id"]


class OfferViewSet(viewsets.ModelViewSet):

    queryset = Offer.objects.all()
    serializer_class = OfferListSerializer

    serializer_action_classes = {
        "list": OfferListSerializer,
        "retrieve": OfferListSerializer,
        "create": OfferCreateSerializer,
        "partial_update": OfferUpdateSerializer,
        "destroy": OfferListSerializer,
    }

    pagination_class = CustomPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = OfferFilter
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]

    def get_queryset(self):
        return Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, self.serializer_class)


class OfferDetailsView(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    http_method_names = ["get", "patch"]

    def list(self, request):
        return Response(status=404)
