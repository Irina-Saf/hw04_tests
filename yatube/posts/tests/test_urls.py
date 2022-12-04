from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_page_index(self):
        """Проверяем доступ к главной странице."""

        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    """Создаем тестовых пользователей, группу и пост."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_no_auth = User.objects.create_user(username='no_auth')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_slug',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_auth = Client()
        self.authorized_client_auth.force_login(self.user)
        self.authorized_client_no_auth = Client()
        self.authorized_client_no_auth.force_login(self.user_no_auth)

    def test_urls_templates(self):
        """Проверяем доступность шаблонов и доступа к страницам для
         авторизованного автора."""

        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create.html',
            '/create/': 'posts/create.html',
        }

        for adress, template in templates_url_names.items():

            with self.subTest(adress=adress):
                response = self.authorized_client_auth.get(adress)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404_url(self):
        """Проверяем, что статус ответа сервера - 404."""

        response_url = {
            self.guest_client: '/unexisting_page/',
        }
        for client, url in response_url.items():
            with self.subTest(client=client):
                response = client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.NOT_FOUND
                )

    def test_urls_templates_no_auth(self):
        """Проверяем доступность шаблонов и доступа к страницам
         для авторизованного не автора."""

        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create.html',
        }

        for adress, template in templates_url_names.items():

            with self.subTest(adress=adress):
                response = self.authorized_client_no_auth.get(adress)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.authorized_client_no_auth.get(
            f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(response, (f'/posts/{self.post.id}/'))

    def test_pages_open_for_guest_client(self):
        """Проверяем доступность шаблонов и доступа к страницам
         для гостевого пользователя, включая переадресацию."""

        templates_url_location = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }

        for adress, template in templates_url_location.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{self.post.id}/edit/'))

    def test_edit_for_authorized_client_no_auth(self):
        """Проверяем переадресацию для авторизованного не автора."""

        response = self.authorized_client_no_auth.get(
            f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(response, (f'/posts/{self.post.id}/'))
