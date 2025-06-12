from rest_framework import serializers
from django.contrib.auth import get_user_model
from reviews_app.models import Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    business_user = serializers.IntegerField(write_only=True)
    business_user_data = serializers.SerializerMethodField(read_only=True)
    reviewer_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer_data",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_business_user_data(self, obj):
        return {
            "id": obj.business_user.id,
            "username": obj.business_user.username,
            "type": obj.business_user.type,
        }

    def get_reviewer_data(self, obj):
        return {
            "id": obj.reviewer.id,
            "username": obj.reviewer.username,
            "type": obj.reviewer.type,
        }

    def validate_business_user(self, value):
        """Validiert dass business_user existiert und type 'business' hat"""
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Business User nicht gefunden.")

        if user.type != "business":
            raise serializers.ValidationError("User muss vom Typ 'business' sein.")

        return value

    def validate(self, attrs):
        """Validiert dass reviewer type 'customer' hat und kein doppeltes Review existiert"""
        request = self.context.get("request")
        reviewer = request.user

        if reviewer.type != "customer":
            raise serializers.ValidationError(
                {"reviewer": "Nur Kunden können Reviews erstellen."}
            )

        # Bei CREATE: Überprüfe ob bereits Review existiert
        if not self.instance:  # CREATE
            business_user_id = attrs.get("business_user")
            if Review.objects.filter(
                business_user_id=business_user_id, reviewer=reviewer
            ).exists():
                raise serializers.ValidationError(
                    {
                        "non_field_errors": "Sie haben bereits ein Review für diesen Business User erstellt."
                    }
                )

        return attrs

    def create(self, validated_data):
        """Erstellt Review mit aktuellem User als reviewer"""
        business_user_id = validated_data.pop("business_user")
        business_user = User.objects.get(id=business_user_id)

        validated_data["business_user"] = business_user
        validated_data["reviewer"] = self.context["request"].user

        return super().create(validated_data)
