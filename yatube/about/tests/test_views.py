from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """При запросе к статическим страницам
        применяется правильные шаблоны."""

        templates_page_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        for reverse_name, template in templates_page_names.items():

            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_access_by_name(self):
        """URL, генерируемый при помощи имен, доступен."""

        templates_views_location = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        for reverse_name in templates_views_location:

            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
