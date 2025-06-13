from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from reviews_app.models import Review

User = get_user_model()


class ReviewTestSetup(APITestCase):
    def setUp(self):
        # Test Users mit Custom User Model erstellen
        self.first_business_user = User.objects.create_user(
            username="business_test",
            email="business@test.com",
            password="testpass123",
            first_name="Max",
            last_name="Muster",
            type="business",
        )

        self.second_business_user = User.objects.create_user(
            username="second_business_test",
            email="secondbusiness@test.com",
            password="testpass123",
            first_name="Fritz",
            last_name="Muster",
            type="business",
        )

        self.first_customer_user = User.objects.create_user(
            username="customer_test",
            email="customer@test.com",
            password="testpass123",
            first_name="Jane",
            last_name="Sonomo",
            type="customer",
        )

        self.second_customer_user = User.objects.create_user(
            username="second_customer_test",
            email="secondcustomer@test.com",
            password="testpass123",
            first_name="Udo",
            last_name="Pommes",
            type="customer",
        )

        # Tokens für Authentication erstellen
        self.first_business_token = Token.objects.create(user=self.first_business_user)
        self.second_business_token = Token.objects.create(
            user=self.second_business_user
        )
        self.first_customer_token = Token.objects.create(user=self.first_customer_user)
        self.second_customer_token = Token.objects.create(
            user=self.second_customer_user
        )

        # APIClient setup
        self.client = APIClient()

    def authenticate_user(self, user_type="business", custom_user_number="1"):
        """Helper method for User Authentication."""
        if user_type == "business" and custom_user_number == "1":
            self.client.credentials(
                HTTP_AUTHORIZATION="Token " + self.first_business_token.key
            )
        elif user_type == "business" and custom_user_number == "2":
            self.client.credentials(
                HTTP_AUTHORIZATION="Token " + self.second_business_token.key
            )
        elif user_type == "customer" and custom_user_number == "1":
            self.client.credentials(
                HTTP_AUTHORIZATION="Token " + self.first_customer_token.key
            )
        elif user_type == "customer" and custom_user_number == "2":
            self.client.credentials(
                HTTP_AUTHORIZATION="Token " + self.second_customer_token.key
            )

    def clear_authentication(self):
        """Helper method remove Authentication."""
        self.client.credentials()


class reviewTest(ReviewTestSetup):

    def setUp(self):
        super().setUp()
        self.types = ["business", "customer"]

        self.first_review_example_post = {
            "business_user": self.first_business_user.id,
            "rating": 4,
            "description": "Alles war toll!",
        }

        self.second_review_example_post = {
            "business_user": self.second_business_user.id,
            "rating": 2,
            "description": "Alles war nicht so toll!",
        }

        self.review_example_patch = {
            "rating": 5,
            "description": "Noch besser als erwartet!",
        }

    def test_get_review_authenticated(self):
        for i in self.types:
            self.authenticate_user( i, "1")
            url = reverse("review-list")

            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.clear_authentication()