from rest_framework import serializers
from django.contrib.auth import get_user_model
from reviews_app.models import Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review , check if business_user == type : 'business'
    """
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    reviewer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

    def validate_business_user(self, value):
        """
        Validiert, dass der business_user den Typ 'business' hat
        """
        if not hasattr(value, 'type') or value.type != 'business':
            raise serializers.ValidationError(
                "Der ausgewählte User muss vom Typ 'business' sein."
            )
        return value