from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, User
from .forms import PostForm

POSTS_PER_PAGE = 10


def index(request):
    templates = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Это главная страница проекта Yatube'
    context = {
        'page_obj': page_obj,
        'title': title
    }
    return render(request, templates, context)


def group_posts(request, slug):
    templates = 'posts/group_list.html'
    post_list = Post.objects.all()
    group = get_object_or_404(Group, slug=slug)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, templates, context)


def profile(request, username):
    template = "posts/profile.html"
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, 10)
    post_count = post_list.count()
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "title": f"Профайл пользователя {username}",
        "author": author,
        "post_count": post_count,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    post = Post.objects.get(id=post_id)
    group = post.group
    title = post.text[0:29]
    post_count = Post.objects.filter(author=post.author).count()
    context = {
        "post": post,
        "title": f"Пост {title}",
        "group": group,
        "post_count": post_count,
        "username": request.user.username,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user == post.author:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)

        return render(request, 'posts/create_post.html',
                      {'form': form, 'is_edit': True})

    return redirect('posts:post_detail', post_id=post_id)
