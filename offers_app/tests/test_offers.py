from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from offers_app.models import Offer, OfferDetail
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import re
from urllib.parse import urlparse


User = get_user_model()


class OfferTestSetup(APITestCase):

    def setUp(self):
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

        self.post_data = {
            "title": "New Offer",
            "description": "This is a new offer.",
            "details": [
                {
                    "title": "Basic Package",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 100.00,
                    "offer_type": "basic",
                    "features": ["Feature 1", "Feature 2"],
                },
                {
                    "title": "Standard Package",
                    "revisions": 3,
                    "delivery_time_in_days": 5,
                    "price": 200.00,
                    "offer_type": "standard",
                    "features": ["Feature 1", "Feature 2", "Feature 3"],
                },
                {
                    "title": "Premium Package",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 300.00,
                    "offer_type": "premium",
                    "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
                },
            ],
        }

        self.patch_data = {
            "title": "Updated Offer",
            "details": [
                {
                    "title": "Basic Package",
                    "revisions": 3,
                    "delivery_time_in_days": 4,
                    "price": 150.00,
                    "offer_type": "basic",
                    "features": ["Feature 1", "Feature 2", "Feature 3"],
                }
            ],
        }

        self.types = ["business", "customer"]

        Offer.objects.create(
            user=self.first_business_user,
            title="Test Offer 1",
            description="This is a test offer for business user 1.",
        )
        OfferDetail.objects.create(
            offer=Offer.objects.get(title="Test Offer 1"),
            title="Basic Package",
            revisions=2,
            delivery_time_in_days=3,
            price=100.00,
            offer_type="basic",
            features=["Feature 1", "Feature 2"],
        )
        OfferDetail.objects.create(
            offer=Offer.objects.get(title="Test Offer 1"),
            title="Standard Package",
            revisions=3,
            delivery_time_in_days=5,
            price=200.00,
            offer_type="standard",
            features=["Feature 1", "Feature 2", "Feature 3"],
        )
        OfferDetail.objects.create(
            offer=Offer.objects.get(title="Test Offer 1"),
            title="Premium Package",
            revisions=5,
            delivery_time_in_days=7,
            price=300.00,
            offer_type="premium",
            features=["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
        )

        # Tokens für Authentication erstellen
        self.first_business_token = Token.objects.create(user=self.first_business_user)
        self.second_business_token = Token.objects.create(
            user=self.second_business_user
        )
        self.first_customer_token = Token.objects.create(user=self.first_customer_user)

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


class OfferListTestCase(OfferTestSetup):

    def test_offer_list(self):
        """
        Test if the offer list is accessible and returns a 200 status code.
        wthout authentication, it should return a 200 status code.
        """

        response = self.client.get(reverse("offers:offers-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # 3 Pagination + 1 results with offers
        self.assertEqual(
            len(response.data["results"]), 1
        )  # Only one offer created in setUp
        self.assertEqual(
            response.data["results"][0]["details"][0]["url"], "/offerdetails/1/"
        )
        self.assertEqual(response.data["count"], 1)

    def test_filtered_offer_list_creator_id(self):
        """
        Test if the offer list can be filtered by creator_id.
        """
        response = self.client.get(
            reverse("offers:offers-list"), {"creator_id": self.first_business_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["count"], 1
        )  # Only one offer created by the first business user
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["user"], self.first_business_user.id
        )

    def test_filtered_offer_list_min_price(self):
        """
        Test if the offer list can be filtered by min_price.
        """
        response = self.client.get(reverse("offers:offers-list"), {"min_price": 90})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filtered_offer_lisat_min_delivery_time(self):
        """
        Test if the offer list can be filtered by min_delivery_time.
        """
        response = self.client.get(
            reverse("offers:offers-list"), {"min_delivery_time": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filtered_offer_list_search(self):
        """
        Test if the offer list can be filtered by search query.
        """
        response = self.client.get(
            reverse("offers:offers-list"), {"search": "Test Offer 1"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Offer 1")


class OfferDetailTestCase(OfferTestSetup):

    def test_offer_detail_with_auth(self):
        """
        Test if the offer detail is accessible and returns a 200 status code.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")

        offer = Offer.objects.get(title="Test Offer 1")
        response = self.client.get(reverse("offers:offers-detail", args=[offer.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Offer 1")
        self.assertEqual(len(response.data["details"]), 3)

        expected_id = OfferDetail.objects.get(offer=offer, offer_type="basic")
        self.assertEqual(response.data["details"][0]["id"], expected_id.id)

        url = response.data["details"][0]["url"]
        self.assertTrue(
            re.match(r"^http://.+/api/offerdetails/\d+/?$", url),
            f"URL {url} stimmt nicht mit dem erwarteten Muster überein",
        )

        parsed = urlparse(url)
        self.assertEqual(parsed.path, f"/api/offerdetails/{expected_id.id}/")

    def test_offer_detail_without_auth(self):
        """
        Test if the offer detail is accessible without authentication.
        """
        offer = Offer.objects.get(title="Test Offer 1")
        response = self.client.get(reverse("offers:offers-detail", args=[offer.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offer_not_found(self):
        """
        Test if a 404 status code is returned when the offer does not exist.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.get(reverse("offers:offers-detail", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferCreateTestCase(OfferTestSetup):

    def setUp(self):
        super().setUp()
        self.post_data_less_details = {
            "title": "New Offer",
            "description": "This is a new offer.",
            "details": [
                {
                    "title": "Basic Package",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 100.00,
                    "offer_type": "basic",
                    "features": ["Feature 1", "Feature 2"],
                },
                {
                    "title": "Standard Package",
                    "revisions": 3,
                    "delivery_time_in_days": 5,
                    "price": 200.00,
                    "offer_type": "standard",
                    "features": ["Feature 1", "Feature 2", "Feature 3"],
                },
            ],
        }

    def test_create_offer_with_details(self):
        """
        Test if an offer can be created with details.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")

        response = self.client.post(
            reverse("offers:offers-list"), self.post_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], self.post_data["title"])
        self.assertEqual(len(response.data["details"]), 3)

    def test_create_offer_without_details(self):
        """
        Test if an offer cannot be created without details.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")

        data = {
            "title": "New Offer Without Details",
            "description": "This offer has no details.",
        }

        response = self.client.post(reverse("offers:offers-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_with_less_details(self):
        """
        Test if an offer cannot be created with less than 3 details.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")

        response = self.client.post(
            reverse("offers:offers-list"), self.post_data_less_details, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_without_authentication(self):
        """
        Test if an offer cannot be created without authentication.
        """
        response = self.client.post(
            reverse("offers:offers-list"), self.post_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_user_not_business(self):
        """
        Test if an offer cannot be created by a user who is not a business.
        """
        self.authenticate_user(user_type="customer", custom_user_number="1")

        response = self.client.post(
            reverse("offers:offers-list"), self.post_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
