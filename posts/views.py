from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'index.html',
         {'page': page}
     )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:11]
    return render(request, 'group.html', {'group': group, 'posts': posts})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_latest = author.posts.all().order_by('-pub_date')
    paginator = Paginator(posts_latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'posts_latest': posts_latest,
        'author': author
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author_id=author.id)
    context = {
        'author': author,
        'post': post
    }
    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect('posts:post', username, post_id)
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author_id=author.id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('posts:post', username, post_id)
    return render(request, 'new.html', {'post': post, 'form': form})
