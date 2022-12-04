from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_urls_templates(self):
        """Проверяем доступность шаблонов для гостевого пользователя."""

        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for adress, template in templates_url_names.items():

            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_about_url_exists_at_desired_location(self):
        """Проверяем доступ к страницам для гостевого пользователя."""

        templates_url_location = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for adress in templates_url_location:

            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)
