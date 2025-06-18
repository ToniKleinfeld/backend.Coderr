from rest_framework import serializers
from django.contrib.auth import get_user_model
from reviews_app.models import Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review, checks if business_user is of type 'business'.
    """
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

    def validate_business_user(self, value):
        """
        Validates that the business_user has the type 'business'
        """
        if not hasattr(value, 'type') or value.type != 'business':
            raise serializers.ValidationError(
                "The selected user must be of type “business”."
            )
        return value