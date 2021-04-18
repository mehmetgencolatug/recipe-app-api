from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def sample_recipe(user, **params):
    """Create and return sample recipe"""
    defaults = {
        "title": "Sample Recipe",
        "time_minutes": 10,
        "price": 5.00
    }

    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(TestCase):
    """Test public recipe with api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that user auth is required to get recipe list"""

        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, 401)


class PrivateRecipeApiTest(TestCase):
    """Test public tags with api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "recipe@user.com",
            "RecUP."
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieve recipes authenticated"""
        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_limited_to_user(self):
        """Test that users can only see their recipes"""
        user2 = get_user_model().objects.create_user("user2@test.com", "Pass2")
        sample_recipe(user2)
        recipe = sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(recipe.title, res.data[0]["title"])
