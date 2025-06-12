from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from auth_app.models import UserProfile
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseUserSetup(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="exampleUsername",
            email="example@mail.de",
            password="examplePassword2",
            type="customer",
        )
        cls.user2 = User.objects.create_user(
            username="businessUser",
            email="business@mail.de",
            password="securePassword123",
            type="business",
        )


class loginTest(BaseUserSetup):

    def setUp(self):
        self.url = reverse("login")
        self.valid_data_customer = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword2",
        }
        self.valid_data_business = {
            "username": "businessUser",
            "email": "business@mail.de",
            "password": "securePassword123",
        }

    def test_login_customer_success(self):
        response = self.client.post(self.url, self.valid_data_customer, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_registration_business_success(self):
        response = self.client.post(self.url, self.valid_data_business, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_registration_password_mismatch(self):
        data = self.valid_data_customer.copy()
        data["password"] = "wrongPassword"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
