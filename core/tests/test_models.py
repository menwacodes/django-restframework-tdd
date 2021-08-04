from django.test import TestCase
from django.contrib.auth import get_user_model


# Test that the helper function for the model can create a new user
class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "test@menwa.com"
        password = "123456"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is lower case"""
        email = 'test@MENWA.COM'

        user = get_user_model().objects.create_user(
            email=email,
            password="123456"
        )

        self.assertEqual(user.email, user.email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testpw123')
