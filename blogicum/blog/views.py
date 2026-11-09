"""View-функции приложения blog."""
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()

POSTS_PER_PAGE = 10


class ProfileForm(UserChangeForm):
    """Форма редактирования профиля без поля пароля."""

    password = None

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


def annotate_posts(posts):
    """Добавить comment_count и предзагрузить связанные таблицы."""
    return posts.select_related(
        'author', 'category', 'location',
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')


def get_published_posts(posts=None):
    """Отфильтровать опубликованные посты с опубликованной категорией."""
    if posts is None:
        posts = Post.objects.all()
    return posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    )


def paginate(request, queryset, per_page=POSTS_PER_PAGE):
    """Вернуть страницу пагинации для queryset."""
    return Paginator(queryset, per_page).get_page(request.GET.get('page'))


def index(request):
    """Главная страница."""
    posts = annotate_posts(get_published_posts())
    return render(
        request,
        'blog/index.html',
        {'page_obj': paginate(request, posts)},
    )


def post_detail(request, post_id):
    """Страница отдельной публикации."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(get_published_posts(), pk=post_id)
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.select_related('author'),
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Страница публикаций отдельной категории."""
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True,
    )
    posts = annotate_posts(get_published_posts(category.posts.all()))
    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': paginate(request, posts)},
    )


def profile(request, username):
    """Страница пользователя."""
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.all()
    if request.user != profile_user:
        posts = get_published_posts(posts)
    posts = annotate_posts(posts)
    return render(
        request,
        'blog/profile.html',
        {'profile': profile_user, 'page_obj': paginate(request, posts)},
    )


@login_required
def edit_profile(request):
    """Редактирование своего профиля."""
    form = ProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    """Создание новой публикации."""
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Редактирование публикации."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)
    form = PostForm(
        request.POST or None, request.FILES or None, instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    """Удаление публикации."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)
    form = PostForm(instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    """Добавление комментария к публикации."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post.id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        raise Http404
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request, 'blog/comment.html', {'form': form, 'comment': comment},
    )


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        raise Http404
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
