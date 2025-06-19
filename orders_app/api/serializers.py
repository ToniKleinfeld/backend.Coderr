from rest_framework import serializers
from django.contrib.auth import get_user_model
from orders_app.models import Order
from offers_app.models import OfferDetail

User = get_user_model()


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model, handles serialization and validation for orders.
    """

    title = serializers.CharField(source="offer_detail.title", read_only=True)
    revisions = serializers.IntegerField(
        source="offer_detail.revisions", read_only=True
    )
    delivery_time_in_days = serializers.IntegerField(
        source="offer_detail.delivery_time_in_days", read_only=True
    )
    price = serializers.DecimalField(
        source="offer_detail.price",
        max_digits=10,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False,
    )
    features = serializers.ListField(source="offer_detail.features", read_only=True)
    offer_type = serializers.CharField(source="offer_detail.offer_type", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new orders, handles validation and creation of orders.
    """

    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=OfferDetail.objects.all(), write_only=True
    )

    class Meta:
        model = Order
        fields = [
            "customer_user",
            "business_user",
            "offer_detail",
            "status",
            "offer_detail_id",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        customer_user = self.context["request"].user
        detail = validated_data.pop("offer_detail_id")
        business_user = detail.offer.user

        order = Order.objects.create(
            user=customer_user,
            offer_detail=detail,
            business_user=business_user,
            **validated_data
        )

        return order
