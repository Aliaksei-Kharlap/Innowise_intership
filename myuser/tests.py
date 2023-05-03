from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import MagicMock, Mock, patch

from myuser.models import User
from myuser import myuser_services

class AccountTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(email="test1@gmail.com", password="admin", username="testuser1", image_s3_path="",
                                 role="admin",
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
        self.assertEqual(User.objects.filter(email="test@gmail.com").first().username, 'testuser')

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

    @patch.object(myuser_services, "boto3")
    def test_image_upload(self, boto3_mock):
        """
        Ensure we can upload image.
        """
        self.client.login(email="test1@gmail.com", password="admin", username="testuser1")
        mock = MagicMock()
        mock.upload_fileobj.return_value = True
        boto3_mock.client.return_value = mock
        mock_file = MagicMock()
        mock_file.content_type = 'image/jpeg'
        url = "/user/users/add_image/"
        response = self.client.post(url, data={'image': mock_file})

        self.assertEqual(response.status_code, 200)
