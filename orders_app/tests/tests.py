from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders_app.models import Order
from offers_app.models import OfferDetail, Offer
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import re
from urllib.parse import urlparse


User = get_user_model()


class OrderTestSetup(TestCase):
    def setUp(self):
        self.first_business_user = User.objects.create_user(
            username="business_test",
            email="business@test.com",
            password="testpass123",
            first_name="Max",
            last_name="Muster",
            type="business",
            is_staff=True,
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

        self.post_data = {"offer_detail_id": 2}

        self.patch_data_one = {"status": "completed"}
        self.patch_data_two = {"status": "in_progress"}

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

        Order.objects.create(
            business_user=self.first_business_user,
            customer_user=self.first_customer_user,
            offer_detail=OfferDetail.objects.get(id=3),
            status="completed",
        )

        # Tokens für Authentication erstellen
        self.first_business_token = Token.objects.create(user=self.first_business_user)
        self.second_business_token = Token.objects.create(user=self.second_business_user)
        self.first_customer_token = Token.objects.create(user=self.first_customer_user)

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


class OrdersListTestCase(OrderTestSetup):

    def test_order_list(self):
        """Test if the order list is accessible."""
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.get(reverse("orders:orders-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "completed")
        self.assertEqual(response.data[0]["business_user"], 1)
        self.assertEqual(len(response.data[0]["features"]), 4)

    def test_order_list_without_authentication(self):
        """Test if the order list is not accessible without authentication."""
        self.clear_authentication()
        response = self.client.get(reverse("orders:orders-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_detail_405(self):
        """Test if the order detail endpoint returns 405 for GET requests."""
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.get(reverse("orders:orders-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class OrdersCreateTestCase(OrderTestSetup):

    def test_order_create(self):
        """Test if an order can be created."""
        self.authenticate_user(user_type="customer", custom_user_number="1")
        response = self.client.post(reverse("orders:orders-list"), self.post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "in_progress")
        self.assertEqual(response.data["business_user"], 1)
        self.assertEqual(response.data["customer_user"], 3)
        self.assertEqual(len(response.data["features"]), 3)

    def test_order_create_wrong_data(self):
        """Test if an order cannot be created with wrong data."""
        self.authenticate_user(user_type="customer", custom_user_number="1")
        wrong_post_data = {"wrong_data": 1}
        response = self.client.post(reverse("orders:orders-list"), wrong_post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("offer_detail_id", response.data)

    def test_order_create_without_authentication(self):
        """Test if an order cannot be created without authentication."""
        self.clear_authentication()
        response = self.client.post(reverse("orders:orders-list"), self.post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_create_with_buissiness_user(self):
        """Test if an order cannot be created by a business user."""
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.post(reverse("orders:orders-list"), self.post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_create_with_invalid_offer_detail_id(self):
        """Test if an order cannot be created with an invalid offer_detail_id."""
        self.authenticate_user(user_type="customer", custom_user_number="1")
        invalid_post_data = {"offer_detail_id": 999}
        response = self.client.post(reverse("orders:orders-list"), invalid_post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrdersPatchTestCase(OrderTestSetup):

    def test_order_patch(self):
        """Test if an order can be updated."""
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.patch(
            reverse("orders:orders-detail", kwargs={"pk": 1}), self.patch_data_two, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "in_progress")

    def test_order_patch_with_wrong_data(self):
        """Test if an order cannot be updated with wrong data."""
        self.authenticate_user(user_type="business", custom_user_number="1")
        wrong_patch_data = {"status": "test"}
        response = self.client.patch(reverse("orders:orders-detail", kwargs={"pk": 1}), wrong_patch_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_patch_without_authentication(self):
        """Test if an order cannot be updated without authentication."""
        self.clear_authentication()
        response = self.client.patch(
            reverse("orders:orders-detail", kwargs={"pk": 1}), self.patch_data_one, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_patch_as_customer_user(self):
        """Test if an order cannot be updated by a customer user."""
        self.authenticate_user(user_type="customer", custom_user_number="1")
        response = self.client.patch(
            reverse("orders:orders-detail", kwargs={"pk": 1}), self.patch_data_one, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_patch_with_invalid_order_id(self):
        """Test if an order cannot be updated with an invalid order ID."""
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.patch(
            reverse("orders:orders-detail", kwargs={"pk": 999}), self.patch_data_one, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrdersDeleteTestCase(OrderTestSetup):

    def test_order_delete(self):
        """Test if an order can be deleted."""
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.delete(reverse("orders:orders-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    def test_order_delete_without_authentication(self):
        """Test if an order cannot be deleted without authentication."""
        self.clear_authentication()
        response = self.client.delete(reverse("orders:orders-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_delete_without_staff_status(self):
        """Test if an order cannot be deleted by a user without staff status."""
        self.authenticate_user(user_type="customer", custom_user_number="1")
        response = self.client.delete(reverse("orders:orders-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_delete_with_invalid_order_id(self):
        """Test if an order cannot be deleted with an invalid order ID."""
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.delete(reverse("orders:orders-detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class Order_countsTestCase(OrderTestSetup):

    def test_order_counts(self):
        """Test if the order counts are correct."""
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.get(reverse("order-count", kwargs={"business_user_id": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 1)

    def test_order_counts_without_authentication(self):
        """Test if the order counts cannot be accessed without authentication."""
        self.clear_authentication()
        response = self.client.get(reverse("order-count", kwargs={"business_user_id": 1}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_counts_with_invalid_business_user_id(self):
        """Test if the order counts cannot be accessed with an invalid business user ID."""
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.get(reverse("order-count", kwargs={"business_user_id": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
