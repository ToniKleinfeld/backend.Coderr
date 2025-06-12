from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model() 


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user", "type"]


class RegistrationsSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        pw = attrs.get("password")
        repeated_pw = attrs.get("repeated_password")
        email = attrs.get("email")

        if pw != repeated_pw:
            raise serializers.ValidationError({"error": "Passwords do not match."})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"error": "Email is already in use."})

        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        
        password = validated_data.pop("password")
        
        user = User.objects.create_user(
            password=password,
            **validated_data 
        )
        return user
