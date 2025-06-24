from rest_framework import viewsets, status, permissions, mixins
from rest_framework.response import Response
from orders_app.api.serializers import OrderSerializer, OrderCreateUpdateSerializer
from orders_app.models import Order
from offers_app.models import OfferDetail
from orders_app.api.permissions import OrdersPermissions
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import get_user_model


User = get_user_model()


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

        offer_detail_id = request.data.get("offer_detail_id")
        if offer_detail_id is not None and not isinstance(offer_detail_id, int):
            return Response({"error": "offer_detail_id must be a number"}, status=status.HTTP_400_BAD_REQUEST)

        if offer_detail_id and not OfferDetail.objects.filter(id=offer_detail_id).exists():
            raise NotFound(f"OfferDetail with ID {offer_detail_id} does not exist.")

        return super().create(request, *args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, self.serializer_class)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCountView(APIView):
    """
    View to get the count of orders for a specific user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id, type="business")

        order_count = Order.objects.filter(business_user=business_user).count()

        return Response({"order_count": order_count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """
    View to get the count of completet orders for a specific user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):

        business_user = get_object_or_404(User, id=business_user_id, type="business")

        completed_order_count = Order.objects.filter(business_user=business_user, status="completed").count()

        return Response({"completed_order_count": completed_order_count}, status=status.HTTP_200_OK)
