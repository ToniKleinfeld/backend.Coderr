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
        self.assertEqual(
            response.data["description"], self.second_review_example_post["description"]
        )
        self.assertEqual(
            response.data["business_user"],
            self.second_review_example_post["business_user"],
        )
        self.assertEqual(
            response.data["rating"], self.second_review_example_post["rating"]
        )

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

        response = self.client.get(
            f"/api/reviews/?business_user__id={self.first_business_user.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        for review in response.data:
            self.assertEqual(review["business_user"], self.first_business_user.id)

    def test_filter_by_reviewer_id(self):

        self.authenticate_user("customer", "1")

        response = self.client.get(
            f"/api/reviews/?reviewer__id={self.first_customer_user.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        for review in response.data:
            self.assertEqual(review["reviewer"], self.first_customer_user.id)

    def test_filter_by_multiple_fields(self):
        self.authenticate_user("customer", "1")

        response = self.client.get(
            f"/api/reviews/?business_user__id={self.first_business_user.id}&reviewer__id={self.first_customer_user.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        review = response.data[0]
        self.assertEqual(review["business_user"], self.first_business_user.id)
        self.assertEqual(review["reviewer"], self.first_customer_user.id)

    def test_filter_no_results(self):
        self.authenticate_user("customer", "1")

        response = self.client.get(
            f"/api/reviews/?business_user__id={self.first_business_user.id}&reviewer__id=999"
        )

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

        response = self.client.get(
            f"/api/reviews/?business_user__id={self.first_business_user.id}&ordering=-rating"
        )

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

        response = self.client.get(
            f"/api/reviews/?business_user__id={self.first_business_user.id}"
        )
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
        self.assertEqual(
            response.data["description"], "Updated review - much better now!"
        )
        updated_review = Review.objects.get(pk=self.review_by_first_customer.pk)
        self.assertEqual(updated_review.rating, 5)
        self.assertEqual(
            updated_review.description, "Updated review - much better now!"
        )

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

        self.assertTrue(
            Review.objects.filter(pk=self.review_by_first_customer.pk).exists()
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Review.objects.filter(pk=self.review_by_first_customer.pk).exists()
        )

    def test_delete_review_by_non_owner_fails(self):
        self.authenticate_user("customer", "2")
        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Review.objects.filter(pk=self.review_by_first_customer.pk).exists()
        )

    def test_business_user_cannot_delete_received_review(self):
        self.authenticate_user("business", "1")
        url = reverse("review-detail", kwargs={"pk": self.review_by_first_customer.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Review.objects.filter(pk=self.review_by_first_customer.pk).exists()
        )

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
        self.assertTrue(
            Review.objects.filter(pk=self.review_by_first_customer.pk).exists()
        )

    def test_delete_review_from_setup_data(self):
        self.authenticate_user("customer", "2")
        setup_review = Review.objects.get(
            business_user=self.first_business_user, reviewer=self.second_customer_user
        )

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
        self.assertTrue(
            Review.objects.filter(pk=self.review_by_second_customer.pk).exists()
        )
