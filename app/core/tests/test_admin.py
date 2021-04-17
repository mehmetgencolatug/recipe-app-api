from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.admin_user = get_user_model().objects.create_superuser(
            email="superuser@mehmettest.com",
            password="SuperTestPass."
        )

        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="testuser@mehmettest.com",
            password="TestPass.",
            name="Test User"
        )

    def test_users_listed(self):
        """Test if users are listed"""
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test user edit page works"""
        url = reverse("admin:core_user_change", args=[self.user.id])
        # /admin/core/user/<id>

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test add user page works"""
        url = reverse("admin:core_user_add")
        # ?? /admin/core/user/add
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
