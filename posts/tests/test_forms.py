from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class YatubeFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='StasBaretskiy')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='Test description')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """Валидная форма создает запись в Post"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Раз, два и три.',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            group=self.group.id,
            text='Раз, два и три.').exists())
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        """При редактировании поста, изменяется запись в базе данных."""
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id,
        }
        test_post = Post.objects.create(
            text='Тестовый текст записи',
            author=self.user,
        )
        posts_count = Post.objects.count()
        kwargs = {'username': self.user.username, 'post_id': test_post.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs=kwargs),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            group=self.group.id,
            text='Измененный текст').exists())
        self.assertRedirects(response, reverse('posts:post', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)
