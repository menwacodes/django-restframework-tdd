from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# rest framework test helper tools
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')  # url to create a user
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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
            "password": "123",
            "name": "menwa"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # returns bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # user wasn't created
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            "email": "test@menwa.com",
            "password": "123456"
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_creds(self):
        """Test that token is not created with invalid creds"""
        create_user(email="test@menwa.com", password="123456")
        payload = {"email": "test@menwa.com", "password": "invalid"}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token isn't created if user doesn't exist"""
        payload = {"email": "test@menwa.com", "password": "123456"}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_password(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {"email": "any", "password": ""})
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # auth is required on manage user end point
    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)
        # no auth, should return unauthed
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""
    def setUp(self) -> None:
        self.user = create_user(
            email='test@menwa.com',
            password='123456',
            name="Test Name"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        # already authenticated in set up
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the /me url"""
        res = self.client.post(ME_URL, {})  # empty object as should fail before data validation

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for auth user"""
        payload = {
            "name": "New Name",
            "password": "newpass123"
        }

        # make request
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
