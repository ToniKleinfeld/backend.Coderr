from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()


class OfferDetailSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        coerce_to_string=False
    )
    class Meta:
        model = OfferDetail
        fields = [
            "id",
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

    def partial_update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class OfferDetailLinkSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "resolver_match"):
            if (
                "list" in request.resolver_match.url_name
                or request.method == "GET"
                and not request.resolver_match.kwargs
            ):
                return f"/offerdetails/{obj.pk}/"

        from django.urls import reverse

        return request.build_absolute_uri(
            reverse("offerdetails:offerdetails-detail", kwargs={"pk": obj.pk})
        )


class OfferListSerializer(serializers.ModelSerializer):

    user_details = UserDetailsSerializer(source="user", read_only=True)
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.FloatField(read_only=True)
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
            "min_delivery_time",
            "min_price",
        ]


class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ["id","title", "image", "description", "details"]
        read_only_fields = ["id"]

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

