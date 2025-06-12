from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from auth_app.models import UserProfile
from rest_framework.authtoken.models import Token
from profiles_app.models import Profile


class ProfileTestSetup(APITestCase):

    def setUp(self):
        # Test Users mit Custom User Model erstellen
        self.business_user = UserProfile.objects.create_user(
            username="business_test",
            email="business@test.com",
            password="testpass123",
            first_name="Max",
            last_name="Muster",
            type="business",
        )

        self.customer_user = UserProfile.objects.create_user(
            username="customer_test",
            email="customer@test.com",
            password="testpass123",
            first_name="Jane",
            last_name="Sonomo",
            type="customer",
        )

        if not hasattr(self.business_user, "profile"):
            Profile.objects.create(user=self.business_user)
        if not hasattr(self.customer_user, "profile"):
            Profile.objects.create(user=self.customer_user)

        # Tokens für Authentication erstellen
        self.business_token = Token.objects.create(user=self.business_user)
        self.customer_token = Token.objects.create(user=self.customer_user)

        # APIClient setup
        self.client = APIClient()

    def authenticate_user(self, user_type="business"):
        """Helper method for User Authentication."""
        if user_type == "business":
            self.client.credentials(
                HTTP_AUTHORIZATION="Token " + self.business_token.key
            )
        elif user_type == "customer":
            self.client.credentials(
                HTTP_AUTHORIZATION="Token " + self.customer_token.key
            )

    def clear_authentication(self):
        """Helper method remove Authentication."""
        self.client.credentials()


class profileTest(ProfileTestSetup):

    def setUp(self):
        super().setUp()
        self.profile_json = {
            "user": 1,
            "username": "",
            "first_name": "",
            "last_name": "",
            "file": "profile_picture.jpg",
            "location": "",
            "tel": "",
            "description": "",
            "working_hours": "",
            "type": "",
            "email": "",
            "created_at": "",
        }
        self.types = ["business", "customer"]

    def test_get_profile_authenticated(self):

        for i in self.types:
            self.authenticate_user(i)

            if i == "business":
                profile = self.business_user.profile
            elif i == "customer":
                profile = self.customer_user.profile

            url = reverse("profile:profile-detail", kwargs={"pk": profile.id})
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            expected_keys = set(self.profile_json.keys())
            response_keys = set(response.data.keys())

            self.assertEqual(expected_keys, response_keys)

            self.assertEqual(response.data["first_name"], profile.first_name)
            self.assertEqual(response.data["location"], "")
            self.assertEqual(response.data["type"], i)
            self.clear_authentication()

    def test_get_profile_unauthenticated(self):
        profile_id = self.business_user.profile.id
        url = reverse("profile:profile-detail", kwargs={"pk": profile_id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_nonexistent_profile(self):
        self.authenticate_user("business")
        url = reverse("profile:profile-detail", kwargs={"pk": 9999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_own_profile_success(self):
        self.authenticate_user("business")

        profile_id = self.business_user.profile.id
        url = reverse("profile:profile-detail", kwargs={"pk": profile_id})

        update_data = {
            "first_name": "Updated Max",
            "location": "München",
            "description": "Updated Business Description",
        }

        response = self.client.patch(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_keys = set(self.profile_json.keys())
        response_keys = set(response.data.keys())
        self.assertEqual(expected_keys, response_keys)

        self.assertEqual(response.data["first_name"], update_data["first_name"])
        self.assertEqual(response.data["location"], update_data["location"])

        # Verify database was updated
        self.business_user.refresh_from_db()
        self.assertEqual(self.business_user.first_name, update_data["first_name"])

    def test_patch_other_user_profile_forbidden(self):

        self.authenticate_user("customer")
        profile_id = self.business_user.profile.id
        url = reverse("profile:profile-detail", kwargs={"pk": profile_id})
        update_data = {
            "first_name": "Hacker Name",
            "location": "München",
            "description": "Updated customer Description",
        }
        response = self.client.patch(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)

    def test_patch_profile_unauthenticated(self):

        profile_id = self.business_user.profile.id
        url = reverse("profile:profile-detail", kwargs={"pk": profile_id})
        update_data = {
            "first_name": "Hacker Name",
            "location": "München",
            "description": "Updated customer Description",
        }
        response = self.client.patch(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileListViewTests(ProfileTestSetup):

    def setUp(self):
        super().setUp()
        self.profile_business_json = {
            "user": 1,
            "username": "",
            "first_name": "",
            "last_name": "",
            "file": "profile_picture.jpg",
            "location": "",
            "tel": "",
            "description": "",
            "working_hours": "",
            "type": "business",
        }
        self.profile_customer_json = {
            "user": 1,
            "username": "",
            "first_name": "",
            "last_name": "",
            "file": "profile_picture.jpg",
            "type": "customer",
        }
        self.types = ["business", "customer"]

    def test_get_profiles_list(self):

        for i in self.types:
            self.authenticate_user(i)
            url = reverse("profiles:" + i + "-profiles-list")
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            if i == "business":
                expected_keys = set(self.profile_business_json.keys())
            elif i == "customer":
                expected_keys = set(self.profile_customer_json.keys())

            response_keys = set(response.data[0].keys())

            self.assertEqual(expected_keys, response_keys)
            self.assertEqual(response.data[0]["username"], i + "_test")
            self.assertEqual(response.data[0]["type"], i)
            self.clear_authentication()

    def test_get_profiles_list_unauthenticated(self):
        for i in self.types:
            url = reverse("profiles:" + i + "-profiles-list")

            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
