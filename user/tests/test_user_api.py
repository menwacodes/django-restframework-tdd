from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# rest framework test helper tools
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')  # url to create a user


# helper function to create users for tests
def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""
    def setup(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            "email": "test@menwa.com",
            "password": "123456",
            "name": "Test name"
        }
        # make request
        res = self.client.post(CREATE_USER_URL, payload)

        # check client returns expected status
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # object is actually created
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))

        # check pw is not returned
        self.assertNotIn('password', res.data)

    # no duplicate users
    def test_user_exists(self):
        """Test creating a user that exists fails"""
        payload = {
            "email": "test@menwa.com",
            "password": "123456"
        }
        create_user(**payload)  # like spread operator in JS
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # password length test
    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {
            "email": "test@menwa.com",
            "password": "123"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # returns bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # user wasn't created
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()

        self.assertFalse(user_exists)
