from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    """Создаем тестовые посты, пользователей, группу и форму."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.user_two = User.objects.create_user(username="Other")
        cls.group = Group.objects.create(
            title='Тест Группа',
            slug='test-slug',
            description='Тест описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тест первый пост',
            group=cls.group
        )

    def setUp(self):
        """Создаем клиент автора и другого пользователя."""

        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)
        self.other_user = Client()
        self.other_user.force_login(self.user_two)

    def cheking_context(self, expect_answer):
        """Проверка контекста страниц"""

        for obj, answer in expect_answer.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, answer)

    def test_create_post_without_group(self):
        """Форма создает запись в Post. Без группы."""

        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый пост без группы текст",
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data
        )
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={
                              "username": PostFormTests.user})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                author=self.user
            ).exists())

    def test_create_post_with_group(self):
        """Форма создает запись в Post. С группой."""

        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый пост с группой текст",
            "group": PostFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data,
        )
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={
                              "username": PostFormTests.user})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                group=form_data["group"],
                author=self.user
            ).exists())

    def test_create_post_with_guest(self):
        """Форма не создает запись в Post от гостя."""

        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст Гостя",
            "group": PostFormTests.group.id,
        }
        self.client.post(reverse("posts:post_create"), data=form_data)
        self.assertEqual(Post.objects.count(), post_count)

    def test_edit_post_with_non_auth(self):
        """Форма не изменяет запись в Post от имени не автора."""

        post_new = Post.objects.create(
            author=PostFormTests.user,
            text="Текст",
        )

        form_data = {
            "text": "Изменение поста не автором текст",
        }
        self.other_user.post(
            reverse(
                "posts:post_edit", kwargs={"post_id": post_new.id},
            ),
            data=form_data,

        )

        post_change = Post.objects.get(
            id=post_new.id,
        )
        expect_answer = {
            post_new.id: post_change.id,
            post_new.text: post_change.text,
            post_new.author: post_change.author,
            post_new.pub_date: post_change.pub_date,
            post_new.group: post_change.group,
        }
        self.cheking_context(expect_answer)

    def test_edit_post_with_group(self):
        """Форма изменяет запись в Post."""
        post_new = Post.objects.create(
            author=PostFormTests.user,
            text="Текст поста автора",
            group=PostFormTests.group
        )
        form_data = {
            "text": "Текст редактирования автором",
            "group": post_new.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": post_new.id},
            ),
            data=form_data,
        )

        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={
                              "post_id": post_new.id})
        )

        post_change = Post.objects.get(id=post_new.id)
        expect_answer = {
            post_new.id: post_change.id,
            form_data["text"]: post_change.text,
            form_data["group"]: post_change.group.id,
            post_new.author: post_change.author,
            post_new.pub_date: post_change.pub_date,

        }
        self.cheking_context(expect_answer)
