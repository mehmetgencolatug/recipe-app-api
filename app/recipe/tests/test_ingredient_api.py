from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse("recipe:ingredient-list")


class PublicIngredientApiTest(TestCase):
    """Test public ingredient with api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that user auth is required to get list"""

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, 401)


class PrivateIngredientApiTest(TestCase):
    """Test public ingredients with api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "tagtest@test.com",
            "IngP."
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test that user auth can see ingredient list"""
        Ingredient.objects.create(user=self.user, name="Cucumber")
        Ingredient.objects.create(user=self.user, name="Chocolate")

        res = self.client.get(INGREDIENT_URL)
        tags = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(tags, many=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_tags_are_limited_to_user(self):
        """Test that users can only see their tags"""
        """Test that user auth can see tags list"""
        user2 = get_user_model().objects \
            .create_user(email="user2@test.com", password="U2Pass.")
        Ingredient.objects.create(user=user2, name="Cucumber")
        ingredient = Ingredient.objects \
            .create(user=self.user, name="Chocolate")

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
