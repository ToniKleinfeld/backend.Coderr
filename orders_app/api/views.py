from rest_framework import viewsets, status, permissions, mixins
from rest_framework.response import Response
from orders_app.api.serializers import OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer
from orders_app.models import Order
from orders_app.api.permissions import OrdersPermissions


class OrderViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for managing Order objects: list, create, update, delete.
    Handles serialization and validation for orders.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    serializer_action_classes = {
        "list": OrderSerializer,
        "create": OrderCreateSerializer,
        "partial_update": OrderUpdateSerializer,
    }
    permission_classes = [OrdersPermissions]

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, self.serializer_class)

    def perform_create(self, serializer):
        serializer.save(customer_user=self.request.user)  # Assuming the user is the customer

    def perform_update(self, serializer):
        serializer.save()  # Save the updated instance
