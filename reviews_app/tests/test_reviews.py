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

        Review.objects.create(
            business_user=self.first_business_user,
            reviewer=self.second_customer_user,
            rating=1,
            description="War schon mal besser",
        )

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

        # Tokens für Authentication erstellen
        self.first_business_token = Token.objects.create(user=self.first_business_user)
        self.second_business_token = Token.objects.create(user=self.second_business_user)
        self.first_customer_token = Token.objects.create(user=self.first_customer_user)
        self.second_customer_token = Token.objects.create(user=self.second_customer_user)

        # APIClient setup
        self.client = APIClient()

    def authenticate_user(self, user_type="business", custom_user_number="1"):
        """Helper method for User Authentication."""
        if user_type == "business" and custom_user_number == "1":
            self.client.credentials(HTTP_AUTHORIZATION="Token " + self.first_business_token.key)
        elif user_type == "business" and custom_user_number == "2":
            self.client.credentials(HTTP_AUTHORIZATION="Token " + self.second_business_token.key)
        elif user_type == "customer" and custom_user_number == "1":
            self.client.credentials(HTTP_AUTHORIZATION="Token " + self.first_customer_token.key)
        elif user_type == "customer" and custom_user_number == "2":
            self.client.credentials(HTTP_AUTHORIZATION="Token " + self.second_customer_token.key)

    def clear_authentication(self):
        """Helper method remove Authentication."""
        self.client.credentials()


class ReviewListTestCase(ReviewTestSetup):
    def test_get_review_authenticated(self):
        for i in self.types:
            self.authenticate_user(i)
            url = reverse("review-list")

            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.clear_authentication()

    def test_get_review_unauthenticated(self):
        url = reverse("review-list")
        detailUrl = reverse("review-detail", kwargs={"pk": 1})
        response = self.client.get(url)
        detailResponse = self.client.get(detailUrl)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(detailResponse.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewCreateTestCase(ReviewTestSetup):
    def test_post_review_business_user_forbidden(self):
        self.authenticate_user(self.types[0])
        url = reverse("review-list")

        response = self.client.post(url, self.second_review_example_post, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_review_success(self):
        self.authenticate_user(self.types[1])
        url = reverse("review-list")

        response = self.client.post(url, self.second_review_example_post, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["description"], self.second_review_example_post["description"])
        self.assertEqual(
            response.data["business_user"],
            self.second_review_example_post["business_user"],
        )
        self.assertEqual(response.data["rating"], self.second_review_example_post["rating"])

    def test_post_review_same_business_user(self):
        self.authenticate_user(self.types[1], "2")
        url = reverse("review-list")

        response = self.client.post(url, self.first_review_example_post, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_review_wrong_data(self):
        self.authenticate_user(self.types[1], "1")
        url = reverse("review-list")
        data = self.first_review_example_post.copy()
        data["rating"] = 7

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
