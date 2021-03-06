from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email="sample_user@test.com", password="SampleP."):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


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

    def test_tag_str(self):
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Vegan",
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient str repr"""

        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Cucumber",
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe str repr"""

        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Stake and mushroom sauce",
            time_minutes=5,
            price=5.0
        )

        self.assertEqual(str(recipe), recipe.title)
