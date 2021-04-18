from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the user API public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating new user with valid payload"""

        payload = {
            "email": "mehmet@mehmettest.com",
            "password": "TestP.",
            "name": "Test Name"
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, 201)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test creating user already exists fails"""

        payload = {
            "email": "mehmet_exists@mehmettest.com",
            "password": "TestP.",
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, 400)

    def password_too_short(self):
        """Test password must be more than 5 characters"""
        payload = {
            "email": "mehmet_password@mehmettest.com",
            "password": "MG",
            "name": "Test Name Short"
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, 400)
        user_exists = get_user_model().objects \
            .filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            "email": "mehmettoken@mehmettest.com",
            "password": "TestP.",
            "name": "Test Name"
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, 200)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created with invalid credentials"""

        payload = {
            "email": "mehmet@mehmettest.com",
            "password": "TestP.",
            "name": "Test Name"
        }
        create_user(**payload)
        payload["password"] = "wrongP."
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, 400)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not exists"""
        payload = {
            "email": "mehmetnouser@mehmettest.com",
            "password": "TestP.",
            "name": "Test Name"
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, 400)

    def test_create_token_empty_fields(self):
        """Test that token is not created if some fields do not exist"""
        payload = {
            "email": "mehmetnopass@mehmettest.com",
            "password": "",
            "name": "Test Name"
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, 400)

    def test_retreive_user_unauthorized(self):
        """Test that authentication is requeired for users"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, 401)


class PrivateUsersApiTest(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email="mehmet@test.com",
            password="testpwd",
            name="Test Name"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retreive_profile_success(self):
        """Test retreiving profile for logged in user"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data,
                         {
                             "name": self.user.name,
                             "email": self.user.email
                         })

    def test_method_not_allowed(self):
        """Test post method is not allowed"""
        res = self.client.post(ME_URL)

        self.assertEqual(res.status_code, 405)

    def test_update_user_profile(self):
        """Test update user profile value for authenticated user"""

        payload = {
            "email": "mehmetupdate@test.com",
            "password": "TestP.",
            "name": "Test Name Updated"
        }

        res = self.client.patch(ME_URL, payload)
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, 200)
