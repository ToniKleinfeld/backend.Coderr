from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from reviews_app.models import Review
from reviews_app.tests.test_reviews import ReviewTestSetup

User = get_user_model()


class ReviewDeleteTestCase(ReviewTestSetup):
    def setUp(self):
        super().setUp()

        self.review_by_first_customer = Review.objects.create(
            business_user=self.first_business_user,
            reviewer=self.first_customer_user,
            rating=4,
            description="Review to be deleted",
        )

        self.review_by_second_customer = Review.objects.create(
            business_user=self.second_business_user,
            reviewer=self.second_customer_user,
            rating=3,
            description="Another review to test permissions",
        )

    def test_successful_review_delete_by_owner(self):
        self.authenticate_user("customer", "1")

        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        self.assertTrue(Review.objects.filter(pk=self.review_by_first_customer.pk).exists())

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=self.review_by_first_customer.pk).exists())

    def test_delete_review_by_non_owner_fails(self):
        self.authenticate_user("customer", "2")
        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(pk=self.review_by_first_customer.pk).exists())

    def test_business_user_cannot_delete_received_review(self):
        self.authenticate_user("business", "1")
        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(pk=self.review_by_first_customer.pk).exists())

    def test_delete_nonexistent_review_fails(self):
        self.authenticate_user("customer", "1")

        url = reverse("review-detail", kwargs={"pk": 9999})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_review_without_authentication_fails(self):

        self.clear_authentication()

        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Review.objects.filter(pk=self.review_by_first_customer.pk).exists())

    def test_delete_review_from_setup_data(self):
        self.authenticate_user("customer", "2")
        setup_review = Review.objects.get(business_user=self.first_business_user, reviewer=self.second_customer_user)

        url = reverse("review-detail", kwargs={"pk": setup_review.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=setup_review.pk).exists())

    def test_multiple_reviews_independence(self):
        self.authenticate_user("customer", "1")
        initial_count = Review.objects.count()

        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), initial_count - 1)
        self.assertTrue(Review.objects.filter(pk=self.review_by_second_customer.pk).exists())
