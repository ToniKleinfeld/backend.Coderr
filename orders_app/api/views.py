from rest_framework import viewsets, status, permissions, mixins
from rest_framework.response import Response
from orders_app.api.serializers import OrderSerializer, OrderCreateUpdateSerializer
from orders_app.models import Order
from offers_app.models import OfferDetail
from orders_app.api.permissions import OrdersPermissions
from rest_framework.exceptions import NotFound


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for managing Order objects: list, create, update, delete.
    Handles serialization and validation for orders.
    """

    queryset = Order.objects.all()

    serializer_action_classes = {
        "list": OrderSerializer,
        "create": OrderCreateUpdateSerializer,
        "partial_update": OrderCreateUpdateSerializer,
    }
    permission_classes = [OrdersPermissions]

    def create(self, request, *args, **kwargs):
        # Prüfe ob offer_detail_id existiert
        offer_detail_id = request.data.get("offer_detail_id")
        if offer_detail_id and not OfferDetail.objects.filter(id=offer_detail_id).exists():
            raise NotFound(f"OfferDetail with ID {offer_detail_id} does not exist.")

        return super().create(request, *args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, self.serializer_class)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
