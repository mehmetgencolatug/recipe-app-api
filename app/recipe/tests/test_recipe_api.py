from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse("recipe:recipe-list")


# api/recipe/recipes


def detail_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])


# api/recipe/recipes/<id>


def sample_tag(user, name="Sample Tag"):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Cinnamon"):
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        """Test viewing the recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.ingredients.add(sample_ingredient(user=self.user))
        recipe.tags.add(sample_tag(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test create recipe api"""

        payload = {
            "title": "New Recipe",
            "time_minutes": 30,
            "price": 10.00
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, 201)
        recipe = Recipe.objects.get(id=res.data["id"])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test recipe with multip le tags"""
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Dessert")
        payload = {
            "title": "New Recipe",
            "time_minutes": 30,
            "price": 10,
            "tags": [tag1.id, tag2.id]
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, 201)
        recipe = Recipe.objects.get(id=res.data["id"])

        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test recipe with multip le ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name="Prawns")
        ingredient2 = sample_ingredient(user=self.user, name="Ginger")
        payload = {
            "title": "New Recipe",
            "time_minutes": 30,
            "price": 10,
            "ingredients": [ingredient1.id, ingredient2.id]
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, 201)
        recipe = Recipe.objects.get(id=res.data["id"])

        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test update recipe with small patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user)

        payload = {"title": "New Title", "tags": [new_tag.id]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        recipe = Recipe.objects.get(id=res.data["id"])
        tags = recipe.tags.all()

        self.assertEqual(recipe.title, "New Title")
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0], new_tag)

    def test_full_update_recipe(self):
        """Test update all fields of recipe"""
        recipe = sample_recipe(user=self.user)
        ingredient1 = sample_ingredient(user=self.user, name="Prawns")
        ingredient2 = sample_ingredient(user=self.user, name="Ginger")
        tag1 = sample_tag(user=self.user, name="Apple")
        tag2 = sample_tag(user=self.user, name="Banana")
        payload = {
            "title": "New Recipe Full",
            "time_minutes": 30,
            "price": 20,
            "ingredients": [ingredient1.id, ingredient2.id],
            "tags": [tag1.id, tag2.id],
        }

        url = detail_url(recipe.id)

        self.client.patch(url, payload)
        # new_recipe = Recipe.objects.get(id=res.data["id"])
        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.time_minutes, payload["time_minutes"])
        self.assertEqual(recipe.price, payload["price"])

        ingredients = recipe.ingredients.all()
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

        tags = recipe.tags.all()
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
