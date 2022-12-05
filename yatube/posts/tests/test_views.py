from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

LIMIT_POST = 10


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Группа 1',
            slug='test-slug',
            description='Тест описание группы'
        )
        cls.post = Post.objects.create(
            text='Тест текст поста',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): (
                'posts/group_list.html'),
            reverse('posts:profile', kwargs=(
                {'username': self.user.username})
            ): ('posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            ('posts/post_detail.html'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            ('posts/create.html'),
            reverse('posts:post_create'): 'posts/create.html',
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse("posts:index"))
        page_obj = response.context["page_obj"]

        self.assertIn(self.post, page_obj)
        self.assertEqual(len(page_obj), len(Post.objects.all()[:LIMIT_POST]))

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        self.group_two = Group.objects.create(
            title='Группа 2',
            slug='test-slug-2',
            description='Тест описание группы 2'
        )
        self.post_two = Post.objects.create(
            text='Тест текст поста 2',
            author=self.user,
            group=self.group_two,
        )

        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs=(
                {"slug": f"{self.group.slug}"}
            )))

        group = response.context["group"]
        self.assertEqual(response.context["group"], self.group)
        page_obj = response.context["page_obj"]
        self.assertIn(self.post, page_obj)

        for post in page_obj:
            self.assertEqual(post.group, group)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse(
            'posts:profile',
            args=[self.user]))

        author = response.context["author"]
        self.assertEqual(author, PostPagesTests.user)
        page_obj = response.context["page_obj"]
        self.assertIn(self.post, page_obj)
        for post in page_obj:
            self.assertEqual(post.author, author)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))

        self.assertEqual(response.context.get('post'), self.post)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""

        response = (self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id})))

        self.assertTrue(response.context["is_edit"])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse(
            'posts:post_create'))

        self.assertFalse(response.context["is_edit"])

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        MAX_POST = 13
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тест Группа',
            slug='test-slug',
            description='тест описание группы'
        )

        objs_post = [
            Post(
                text=f'Тестовый текст{i}',
                author=cls.user,
                group=cls.group
            )
            for i in range(MAX_POST)]
        Post.objects.bulk_create(objs_post)

    def test_first_page_contains(self):
        """Проверяем первую станицу пагинатора."""

        url_names = {
            reverse('posts:index'): LIMIT_POST,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): LIMIT_POST,
            reverse(
                'posts:profile',
                args=[self.user]
            ): LIMIT_POST,
        }
        for value, expected in url_names.items():
            with self.subTest(value=value):
                response = self.client.get(f'{value}?page=1')
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):
        """Проверяем вторую станицу пагинатора."""

        LIMIT_SECOND_PAGE = 3
        url_names = {
            reverse(
                'posts:index'
            ): LIMIT_SECOND_PAGE,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): LIMIT_SECOND_PAGE,
            reverse(
                'posts:profile',
                args=[self.user]
            ): LIMIT_SECOND_PAGE,
        }
        for value, expected in url_names.items():
            with self.subTest(value=value):
                response = self.client.get(f'{value}?page=2')
                self.assertEqual(len(response.context['page_obj']), expected)
