from rest_framework import serializers
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail
from rest_framework.response import Response


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method in ("PATCH", "PUT"):
            self.fields["offer_type"].read_only = True

    def create(self, validated_data):
        return OfferDetail.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class OfferDetailLinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ["id", "url"]
        extra_kwargs = {
            "url": {"view_name": "offerdetail-detail", "lookup_field": "pk"}
        }


class OfferListSerializer(serializers.ModelSerializer):

    user_details = UserDetailsSerializer(source="user", read_only=True)
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "user_details",
        ]


class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ["title", "image", "description", "details"]

    def create(self, validated_data):
        details_data = validated_data.pop("details")

        user = self.context["request"].user
        offer = Offer.objects.create(user=user, **validated_data)

        detail_serializer = OfferDetailSerializer(
            data=details_data,
            many=True,
            context=self.context,
        )
        detail_serializer.is_valid(raise_exception=True)
        detail_serializer.save(offer=offer)

        return offer


class OfferUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ["title", "image", "description", "details"]

    def partial_update(self, request, *args, **kwargs):
        offer = self.get_object()
        details_data = request.data.get("details", [])

        super().partial_update(request, *args, **kwargs)

        for detail_data in details_data:
            offer_type = detail_data.get("offer_type")
            detail_instance = OfferDetail.objects.get(
                offer=offer, offer_type=offer_type
            )

            serializer = OfferDetailSerializer(
                detail_instance,
                data=detail_data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(self.get_serializer(offer).data)
