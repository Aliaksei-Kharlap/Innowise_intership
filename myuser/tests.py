from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import MagicMock, Mock

from myuser.models import User

class AccountTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(email="test1@gmail.com", password="admin", username="testuser1", image_s3_path="",
                                 role="user",
                                 title="Some test title1")


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_create_user(self):
        """
        Ensure we can create a new account object.
        """

        url = "/user/users/"
        data = {
                "email": "test@gmail.com",
                "password": "admin",
                "username": "testuser",
                "image_s3_path": "",
                "role": "user",
                "title": "Some test title",
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(pk=2).username, 'testuser')

    def test_login(self):
        """
        Ensure we can log in.
        """
        url = "/user/auth/"

        data = {
                "email": "test1@gmail.com",
                "password": "admin",
                }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.data["email"], "test1@gmail.com")


    def test_image_upload(self):
        """
        Ensure we can upload image.
        """
        url = "/user/users/add_image/"
        mock = Mock()
        mock.return_value = "Success"

        self.client.post = mock
        response = self.client.post(url, "file")

        self.assertEqual(response, "Success")


