from offers_app.tests.test_offers_get_post import OfferTestSetup
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


class OfferUpdateTestCase(OfferTestSetup):

    def test_patch_offer(self):
        """
        Test if an offer can be updated with PATCH method.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")

        offer = Offer.objects.get(title="Test Offer 1")
        response = self.client.patch(
            reverse("offers:offers-detail", args=[offer.id]),
            self.patch_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.patch_data["title"])
        self.assertEqual(len(response.data["details"]), 3)
        self.assertEqual(
            response.data["details"][0]["title"], self.patch_data["details"][0]["title"]
        )
        self.assertEqual(
            response.data["details"][0]["delivery_time_in_days"],
            self.patch_data["details"][0]["delivery_time_in_days"],
        )

    def test_patch_offer_without_authentication(self):
        """
        Test if an offer cannot be updated without authentication.
        """
        offer = Offer.objects.get(title="Test Offer 1")
        response = self.client.patch(
            reverse("offers:offers-detail", args=[offer.id]),
            self.patch_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_offer_user_not_business(self):
        """
        Test if an offer cannot be updated by a user who is not a business.
        """
        self.authenticate_user(user_type="customer", custom_user_number="1")

        offer = Offer.objects.get(title="Test Offer 1")
        response = self.client.patch(
            reverse("offers:offers-detail", args=[offer.id]),
            self.patch_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_other_buisiness_offer(self):
        """
        Test if a business user cannot update an offer created by another business user.
        """
        self.authenticate_user(user_type="business", custom_user_number="2")

        offer = Offer.objects.get(title="Test Offer 1")
        response = self.client.patch(
            reverse("offers:offers-detail", args=[offer.id]),
            self.patch_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_offer_not_found(self):
        """
        Test if a 404 status code is returned when the offer does not exist.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.patch(
            reverse("offers:offers-detail", args=[9999]),
            self.patch_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferDeleteTestCase(OfferTestSetup):

    def test_delete_offer_without_authentication(self):
        """
        Test if an offer cannot be deleted without authentication.
        """
        offer = Offer.objects.get(title="Test Offer 1")
        response = self.client.delete(reverse("offers:offers-detail", args=[offer.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_other_business_offer(self):
        """
        Test if a business user cannot delete an offer created by another business user.
        """
        self.authenticate_user(user_type="business", custom_user_number="2")

        offer = Offer.objects.get(title="Test Offer 1")
        response = self.client.delete(reverse("offers:offers-detail", args=[offer.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_user_not_business(self):
        """
        Test if a customer user cannot delete an offer.
        """
        self.authenticate_user(user_type="customer", custom_user_number="1")

        offer = Offer.objects.get(title="Test Offer 1")
        response = self.client.delete(reverse("offers:offers-detail", args=[offer.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_not_found(self):
        """
        Test if a 404 status code is returned when trying to delete a non-existing offer.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.delete(reverse("offers:offers-detail", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_without_authentication(self):
        """
        Test if an offer cannot be deleted without authentication.
        """
        offer = Offer.objects.get(title="Test Offer 1")
        response = self.client.delete(reverse("offers:offers-detail", args=[offer.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_offer(self):
        """
        Test if an offer can be deleted by the creator.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")

        offer = Offer.objects.get(title="Test Offer 1")
        response = self.client.delete(reverse("offers:offers-detail", args=[offer.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check if the offer is actually deleted
        with self.assertRaises(Offer.DoesNotExist):
            Offer.objects.get(id=offer.id)
