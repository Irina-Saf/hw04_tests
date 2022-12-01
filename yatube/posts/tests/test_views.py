from django import forms
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тест Группа',
            slug='test-slug',
            description='Тест описание группы'
        )
        cls.post = Post.objects.create(
            text='Тест текст поста',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):

        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):

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

        response = self.authorized_client.get(reverse('posts:index'))
        for post in Post.objects.select_related('group'):
            self.assertEqual(response.context.get('post'), post)

    def test_group_list_pages_show_correct_context(self):

        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))

        group = get_object_or_404(Group, slug=self.group.slug)
        first_objects = group.posts.all()

        for post in first_objects:
            self.assertEqual(response.context.get('post'), post)
        second_object = response.context.get('page_obj').object_list
        for post in second_object:
            self.assertEqual(response.context.get('post'), post)

    def test_profile_pages_show_correct_context(self):

        response = self.authorized_client.get(reverse(
            'posts:profile',
            args=[self.user]))

        author = self.user
        first_objects = author.posts.all()
        for post in first_objects:
            self.assertEqual(response.context.get('post'), post)
        second_object = response.context.get('page_obj').object_list
        for post in second_object:
            self.assertEqual(response.context.get('post'), post)

    def test_post_detail_pages_show_correct_context(self):

        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))

        self.assertEqual(response.context.get('post'), self.post)

    def test_post_edit_show_correct_context(self):

        response = (self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id})))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):

        response = self.authorized_client.get(reverse(
            'posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_right_group_exists(self):

        response = self.authorized_client.get(
            reverse('posts:index'))

        object = self.group.posts.filter(
            group=response.context.get('post').group
        )
        self.assertTrue(object.exists())
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))

        object = self.group.posts.filter(
            group=response.context.get('post').group)

        self.assertTrue(object.exists())

    def test_post_right_group(self):
        response = self.authorized_client.get(
            reverse('posts:index'))

        for post in Post.objects.select_related("group"):
            self.assertEqual(response.context.get('post').group, post.group)
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))

        object = self.group.posts.all()
        for post in object:
            self.assertEqual(response.context.get('post').group, post.group)


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
        for i in range(0, MAX_POST):
            cls.post = Post.objects.create(
                text=f'Тестовый текст{i}',
                author=cls.user,
                group=cls.group
            )

    def test_first_page_contains(self):

        LIMIT_POST = 10

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
                response = self.client.get(value + '?page=1')
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):

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
                response = self.client.get(value + '?page=2')
                self.assertEqual(len(response.context['page_obj']), expected)
