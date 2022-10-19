from unittest.mock import Mock

from mysite import settings


import pytest
from rest_framework import status
from rest_framework.test import APITestCase
from facebookk.models import Page
from myuser.models import User

class FacebookkTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(email="test1@gmail.com", password="admin", username="testuser1", image_s3_path="",
                                 role="admin",
                                 title="Some test title1")


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_create_page(self):
        """
        Ensure we can create a new page.
        """

        url = "/pages/"
        data = {
            "name": "Secoddnd page2",
            "uuid": "dsfsdfsssdddds222sss",
            "description": "sdssssss2sssssssssssssssssssssss",
            "tags": [],
            "owner": 1,
            "followers": [],
            "image": None,
            "is_private": False,
            "follow_requests": [],
            "unblock_date": None
            }

        a = User.objects.get(pk=1)
        self.client.force_login(user=a)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Page.objects.count(), 1)
        self.assertEqual(Page.objects.get(pk=1).name, 'Secoddnd page2')


    def test_get_page(self):
        """
        Ensure we can get page.
        """
        user = User.objects.get(pk=1)
        Page.objects.create(**{
            "name": "Secoddnd page2",
            "uuid": "dsfsdfsssdddds222sss",
            "description": "sdssssss2sssssssssssssssssssssss",

            "owner": user,

            "image": None,
            "is_private": False,

            "unblock_date": None
            })

        url = "/pages/2/"
        response = self.client.get(url)
        self.assertEqual(response.data["name"], "Secoddnd page2")


    def test_microservices(self):
        """
        Ensure we can upload image.
        """
        url = "/pages/1/get_statistics/"
        mock = Mock()
        mock.return_value = {
            "posts_count": 1,
            "followers_count" :2,
            "likes_count": 100,
            }

        self.client.get = mock
        response = self.client.get(url)

        self.assertEqual(response["posts_count"], 1)

@pytest.fixture
def page_example(self):
    page = {
            "name": "Secoddnd page2",
            "uuid": "dsfsdfsssdddds222sss",
            "description": "sdssssss2sssssssssssssssssssssss",

            "owner": 1,

            "image": None,
            "is_private": False,

            "unblock_date": None
            }

    return page

def test_create_page(page_example):
    Page.objects.create(**page_example)
    val = Page.objects.get(uuid="dsfsdfsssdddds222sss").name
    assert val == "Secoddnd page2"










