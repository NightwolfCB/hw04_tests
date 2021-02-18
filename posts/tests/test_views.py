from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class YatubeViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Ремонт от Стаса',
            slug='remont_ot_stasa',
            description='Pемонт своими руками'
        )
        cls.user = User.objects.create_user(username='StasBaretskiy')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Старые навыки не пропадают, понимаешь.',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('posts:index'),
            'new.html': reverse('posts:new_post'),
            'group.html': (
                reverse('posts:group', kwargs={'slug': self.group.slug})
            ),
            'posts/post.html':
                reverse('posts:post', kwargs={'username': self.user.username,
                                              'post_id': 1}),
            'posts/profile.html':
                reverse('posts:profile',
                        kwargs={'username': self.user.username}),
            'new.html':
                reverse('posts:post_edit',
                        kwargs={'username': self.user.username,
                                'post_id': 1})
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:index'))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0.username, self.user.username)
    
    def test_group_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
                reverse('posts:group', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context.get('group').title, self.group.title)
        self.assertEqual(response.context.get('group').description,
                         self.group.description)
        self.assertEqual(response.context.get('group').slug, self.group.slug)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_shows_in_index_page(self):
        """Созданный пост с указанной группой появляется на главной
        странице сайта"""
        response = self.authorized_client.get(reverse('posts:index'))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0.username, self.user.username)

    def test_post_shows_in_correct_group(self):
        """Созданный пост находится на странице выбранной группы"""
        group_wrong = Group.objects.create(
            title='Лестница стремянка',
            slug='test_group_wrong',
            description='Падение шансонье'
        )
        response_wrong = self.authorized_client.get(
                reverse('posts:group', kwargs={'slug': group_wrong.slug})
        )
        self.assertNotIn(self.post, response_wrong.context['posts'])

    def test_post_edit_page_show_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом"""
        response = self.authorized_client.get(f'/{self.user.username}/'
                                              f'{self.post.id}/edit/')
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
    
    def test_profile_page_show_correct_context(self):
        """Шаблон профиля пользователя сформирован с правильным контекстом"""
        response = self.authorized_client.get(f'/{self.user.username}/')
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0.username, self.user.username)

    def test_post_page_show_correct_context(self):
        """Шаблон поста сформирован с правильным контекстом"""
        response = self.authorized_client.get(f'/{self.user.username}/'
                                              f'{self.post.id}/')
        post_text = response.context.get('post').text
        post_author = response.context.get('post').author
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author.username, self.user.username)
