from offers_app.tests.test_offers_get_post import OfferTestSetup
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from offers_app.models import Offer, OfferDetail
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class OfferDetails_detailTestCase(OfferTestSetup):

    def test_offer_details_detail_with_auth(self):
        """
        Test if the offer details can be accessed and returns a 200 status code.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")

        offer = Offer.objects.get(title="Test Offer 1")
        detail = OfferDetail.objects.get(offer=offer, offer_type="basic")
        response = self.client.get(
            reverse("offerdetails:offerdetails-detail", args=[detail.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Basic Package")

    def test_offer_details_detail_without_auth(self):
        """
        Test if the offer details cannot be accessed without authentication.
        """
        offer = Offer.objects.get(title="Test Offer 1")
        detail = OfferDetail.objects.get(offer=offer, offer_type="basic")
        response = self.client.get(
            reverse("offerdetails:offerdetails-detail", args=[detail.id])
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offer_details_not_found(self):
        """
        Test if a 404 status code is returned when the offer detail does not exist.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")
        response = self.client.get(
            reverse("offerdetails:offerdetails-detail", args=[9999])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_offer_details_list(self):
        """
        Test if the offer details list is accessible and returns a 404 status code.
        """
        self.authenticate_user(user_type="business", custom_user_number="1")

        response = self.client.get(reverse("offerdetails:offerdetails-list"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_offer_details_list_without_auth(self):
        """
        Test if the offer details list is accessible without authentication.
        """
        response = self.client.get(reverse("offerdetails:offerdetails-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
