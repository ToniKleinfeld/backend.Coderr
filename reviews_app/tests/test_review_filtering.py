from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from reviews_app.models import Review
from reviews_app.tests.test_reviews import ReviewTestSetup

User = get_user_model()


class ReviewFilterAndOrderingTestCase(ReviewTestSetup):
    def setUp(self):
        super().setUp()

        Review.objects.create(
            business_user=self.first_business_user,
            reviewer=self.first_customer_user,
            rating=5,
            description="Excellent service!",
        )

        Review.objects.create(
            business_user=self.second_business_user,
            reviewer=self.first_customer_user,
            rating=3,
            description="Average experience",
        )

        Review.objects.create(
            business_user=self.second_business_user,
            reviewer=self.second_customer_user,
            rating=4,
            description="Pretty good",
        )

    def test_filter_by_business_user_id(self):

        self.authenticate_user("customer", "1")

        response = self.client.get(f"/api/reviews/?business_user_id={self.first_business_user.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        for review in response.data:
            self.assertEqual(review["business_user"], self.first_business_user.id)

    def test_filter_by_reviewer_id(self):

        self.authenticate_user("customer", "1")

        response = self.client.get(f"/api/reviews/?reviewer_id={self.first_customer_user.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        for review in response.data:
            self.assertEqual(review["reviewer"], self.first_customer_user.id)

    def test_filter_by_multiple_fields(self):
        self.authenticate_user("customer", "1")

        response = self.client.get(
            f"/api/reviews/?business_user_id={self.first_business_user.id}&reviewer_id={self.first_customer_user.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        review = response.data[0]
        self.assertEqual(review["business_user"], self.first_business_user.id)
        self.assertEqual(review["reviewer"], self.first_customer_user.id)

    def test_filter_no_results(self):
        self.authenticate_user("customer", "1")

        response = self.client.get(f"/api/reviews/?business_user_id={self.first_business_user.id}&reviewer_id=999")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_ordering_by_rating_ascending(self):
        self.authenticate_user("customer", "1")

        response = self.client.get("/api/reviews/?ordering=rating")

        self.assertEqual(response.status_code, 200)
        ratings = [review["rating"] for review in response.data]
        self.assertEqual(ratings, sorted(ratings))
        self.assertEqual(response.data[0]["rating"], 1)

    def test_ordering_by_rating_descending(self):
        self.authenticate_user("customer", "1")

        response = self.client.get("/api/reviews/?ordering=-rating")

        self.assertEqual(response.status_code, 200)
        ratings = [review["rating"] for review in response.data]
        self.assertEqual(ratings, sorted(ratings, reverse=True))
        self.assertEqual(response.data[0]["rating"], 5)

    def test_ordering_by_updated_at_ascending(self):
        self.authenticate_user("customer", "1")

        response = self.client.get("/api/reviews/?ordering=updated_at")

        self.assertEqual(response.status_code, 200)
        updated_dates = [review["updated_at"] for review in response.data]
        self.assertEqual(updated_dates, sorted(updated_dates))

    def test_ordering_by_updated_at_descending(self):
        self.authenticate_user("customer", "1")

        response = self.client.get("/api/reviews/?ordering=-updated_at")

        self.assertEqual(response.status_code, 200)

        updated_dates = [review["updated_at"] for review in response.data]
        self.assertEqual(updated_dates, sorted(updated_dates, reverse=True))

    def test_combined_filter_and_ordering(self):
        self.authenticate_user("customer", "1")

        response = self.client.get(f"/api/reviews/?business_user_id={self.first_business_user.id}&ordering=-rating")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        for review in response.data:
            self.assertEqual(review["business_user"], self.first_business_user.id)

        ratings = [review["rating"] for review in response.data]
        self.assertEqual(ratings, sorted(ratings, reverse=True))
        self.assertEqual(response.data[0]["rating"], 5)
        self.assertEqual(response.data[1]["rating"], 1)

    def test_invalid_ordering_field(self):
        self.authenticate_user("customer", "1")

        response = self.client.get("/api/reviews/?ordering=invalid_field")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_filtering_requires_authentication(self):
        self.clear_authentication()

        response = self.client.get(f"/api/reviews/?business_user__id={self.first_business_user.id}")
        self.assertEqual(response.status_code, 401)

    def test_ordering_requires_authentication(self):
        self.clear_authentication()

        response = self.client.get("/api/reviews/?ordering=rating")
        self.assertEqual(response.status_code, 401)

    def test_empty_filter_returns_all_reviews(self):
        self.authenticate_user("customer", "1")

        response = self.client.get("/api/reviews/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
