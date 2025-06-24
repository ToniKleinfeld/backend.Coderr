from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from reviews_app.models import Review
from reviews_app.tests.test_reviews import ReviewTestSetup

User = get_user_model()


class ReviewUpdateTestCase(ReviewTestSetup):
    def setUp(self):
        super().setUp()

        self.review_by_first_customer = Review.objects.create(
            business_user=self.first_business_user,
            reviewer=self.first_customer_user,
            rating=3,
            description="Initial review",
        )

        self.review_by_second_customer = Review.objects.create(
            business_user=self.second_business_user,
            reviewer=self.second_customer_user,
            rating=2,
            description="Another initial review",
        )

    def test_successful_review_update_by_owner(self):
        self.authenticate_user("customer", "1")  # first_customer_user

        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        update_data = {
            "rating": 5,
            "description": "Updated review - much better now!",
        }

        response = self.client.patch(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["description"], "Updated review - much better now!")
        updated_review = Review.objects.get(pk=self.review_by_first_customer.pk)
        self.assertEqual(updated_review.rating, 5)
        self.assertEqual(updated_review.description, "Updated review - much better now!")

    def test_partial_review_update_rating_only(self):
        self.authenticate_user("customer", "1")

        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        update_data = {
            "rating": 4,
        }

        response = self.client.patch(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 4)
        self.assertEqual(response.data["description"], "Initial review")

    def test_partial_review_update_description_only(self):
        self.authenticate_user("customer", "1")

        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        update_data = {
            "description": "Updated description only",
        }

        response = self.client.patch(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "Updated description only")
        self.assertEqual(response.data["rating"], 3)

    def test_update_review_by_non_owner_fails(self):
        self.authenticate_user("customer", "2")
        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        update_data = {
            "rating": 1,
            "description": "Trying to update someone else's review",
        }

        response = self.client.patch(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        original_review = Review.objects.get(pk=self.review_by_first_customer.pk)
        self.assertEqual(original_review.rating, 3)
        self.assertEqual(original_review.description, "Initial review")

    def test_update_review_invalid_rating(self):
        self.authenticate_user("customer", "1")

        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        update_data = {
            "rating": 6,
        }

        response = self.client.patch(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_review_forbidden_fields_ignored(self):
        self.authenticate_user("customer", "1")

        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        update_data = {
            "rating": 4,
            "description": "Updated review",
            "business_user": self.second_business_user.id,
            "reviewer": self.second_customer_user.id,
        }

        response = self.client.patch(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 4)
        self.assertEqual(response.data["description"], "Updated review")
        self.assertEqual(response.data["business_user"], self.first_business_user.id)
        self.assertEqual(response.data["reviewer"], self.first_customer_user.id)

    def test_update_nonexistent_review_fails(self):
        self.authenticate_user("customer", "1")

        url = reverse("review-detail", kwargs={"pk": 9999})

        update_data = {
            "rating": 5,
        }

        response = self.client.patch(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_review_without_authentication_fails(self):
        self.clear_authentication()

        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        update_data = {
            "rating": 5,
        }

        response = self.client.patch(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
