from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_user_with_email_successful(self):
        "Test creating a new user with an email is successful"
        email = "mehmet@testemail.com"
        password = "testPass123."

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_noemalized(self):
        """Test the email for new user is normalized or not"""
        email = "mehmet@TEST_NORMALIZE.cOM"
        user = get_user_model().objects. \
            create_user(email=email, password="dummypass")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test user creation with no email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "testpwd")

    def test_create_new_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            email="superuser@mehmettest.com",
            password="superUserPass."
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
