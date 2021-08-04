from django.test import TestCase, Client
# Client allows making tests against application
from django.contrib.auth import get_user_model
from django.urls import reverse

class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.admin_user = get_user_model().objects.create_superuser(
            email="menwa.codes@gmail.com",
            password="homer123"
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email="test@menwa.com",
            password="123456",
            name="Test user full name"
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        # below also checks that HTTP response is 200
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)
