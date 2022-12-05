from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()

POST_TITLE_LENGHT = 15


class PostModelTest(TestCase):
    """Создаем тестовые посты и пользователей."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст проверяемого поста больше 15 символов',
        )

    def test_post_models_have_correct_object_names(self):
        """Проверяем корректное имя поста."""

        post = PostModelTest.post
        expected_object_name = post.text[:POST_TITLE_LENGHT]
        self.assertEqual(str(post), expected_object_name)


class GroupModelTest(TestCase):
    """Создаем тестовые группы."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_models_have_correct_object_names(self):
        """Проверяем корректное имя группы."""

        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
