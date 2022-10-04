import os

from django.shortcuts import render
from django.http import HttpResponseRedirect as redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.exceptions import ObjectDoesNotExist

from .forms import PostForm, TagSelectionForm, SearchForm
from .models import Post, Tag, Like
from .util import LATEST_MAX_POSTS, LIKED_MAX_POSTS, MAIN_MAX_POSTS
from .util import user_token, get_posts_for_user, check_user_token_valid, check_cookie


def get_tag_link(form, match=False):
    match = "&match=1" if match else ''
    return f'filter={",".join(map(str, form.cleaned_data.get("categories")))}{match}'


# debug
def show(request):
    raise Exception


def js(request):
    return render(request, 'news/js.html')


# views
def index(request):
    form = SearchForm()
    token = user_token(request.user)

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            return redirect(f'/news/search?{get_tag_link(form, "fsort" in request.POST.keys())}')

    latest_news = Post.objects.filter(is_posted=True).order_by('-creation_date').all()[:LATEST_MAX_POSTS]
    if request.user.is_authenticated:
        liked_news = [
            like.post for like in Like.objects.filter(user=request.user).order_by('-id').all()[:LIKED_MAX_POSTS]
        ]
    else:
        liked_news = None
    main_posts = get_posts_for_user(request.user)[:MAIN_MAX_POSTS]
    data = {
        'form': form,
        'latest': latest_news,
        'liked': liked_news,
        'main_posts': main_posts,
    }
    response = render(request, 'news/main_posts.html', context=data)
    check_cookie(request, response, token)
    return response


def view_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except ObjectDoesNotExist:
        return redirect('/news/')
    token = user_token(request.user)

    data = {
        'form': None,
        'post': post,
    }

    response = render(request, 'news/view_post.html', context=data)
    check_cookie(request, response, token)
    return response


@login_required
def my_posts(request):
    form = TagSelectionForm()
    list_posts = []
    posts = Post.objects.filter(author=request.user).all()
    if request.method == 'POST':
        form = TagSelectionForm(request.POST)
        print(request.POST.keys())
        if form.is_valid():
            # fsort in request means it's a match search
            return redirect(f"/news/my_posts?{get_tag_link(form, 'fsort' in request.POST.keys())}")
    if 'filter' in request.GET.keys():
        tag_str = request.GET.get('filter').split(',')
        tags = []
        for tag in Tag.objects.all():
            if tag.__str__() in tag_str:
                tags.append(tag)
        form = TagSelectionForm(initial={
            'categories': tags,
        })
        if tags:
            for post in posts:
                post_tags = post.tags.all()
                checks = [tag in post_tags for tag in tags]
                check = all(checks) if request.GET.get('match') else any(checks)
                if check:
                    list_posts.append(post)
            if not list_posts:
                # made for showing no posts if filter goes 0 posts
                posts = None
    data = {
        'posts': list_posts or posts,
        'form': form,
    }

    return render(request, 'news/my_posts.html', context=data)


@login_required
def edit_post(request, post_id):
    def delete_post_image(image):
        try:
            os.remove(image.path)
        except Exception as e:
            print(f'[ERROR] Deleting file: {image.path}, {e.__str__()}')

    try:
        post = Post.objects.get(pk=post_id)
    except ObjectDoesNotExist:
        return redirect('/news/my_posts')
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет доступа для редактирования этой новости')
        return redirect('/news/my_posts')
    form = PostForm(initial={
        'title': post.title,
        'content': post.content,
        'categories': post.tags.all(),
    })
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            f_data = form.cleaned_data
            post.title = f_data.get('title')
            post.content = f_data.get('content')

            if request.FILES.get('image'):
                if post.image:
                    delete_post_image(post.image)
                post.image = request.FILES.get('image')

            tags = f_data.get('categories')
            if list(post.tags.all()) != list(tags):
                post.tags.clear()
                [post.tags.add(tag) for tag in tags]

            post.last_edit_time = timezone.now()
            if any([req in request.POST.keys() for req in ['post', 'hide', 'delete']]):
                if 'delete' in request.POST.keys():
                    if post.image:
                        delete_post_image(post.image)
                    post.delete()
                    messages.info(request, f'Новость с ID: {post_id} успешно была удалена')
                    return redirect('/news/my_posts')
                post.is_posted = 'post' in request.POST.keys()
            post.save()
            messages.success(request, f'Новость с ID: {post_id} успешно была отредактирована')
            return redirect('/news/my_posts')
    data = {
        'form': form,
        'edit_mode': True,
        'is_posted': post.is_posted,
    }

    return render(request, 'news/post.html', context=data)


@login_required
def new_post(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST)
        if any([i in request.POST.keys() for i in ('save', 'post')]):
            if form.is_valid():
                data = form.cleaned_data
                _new = Post(
                    title=data.get('title'),
                    content=data.get('content'),
                    author=request.user,
                )
                _new.is_posted = 'post' in request.POST.keys()
                _new.save()
                if request.FILES.get('image'):
                    file: TemporaryUploadedFile = request.FILES.get('image')
                    _new.image = file
                    _new.save()
                for tag in data.get('categories'):
                    _new.tags.add(tag)
                if 'post' in request.POST.keys():
                    messages.success(request, 'Ваша запись была отпубликована')
                else:
                    messages.success(request, 'Ваша запись была сохранена')
                return redirect('/news/my_posts')
        else:
            messages.error(request, 'Неизвестное действие')

    data = {
        'form': form,
        'edit_mode': False,
        'is_posted': False,
    }
    return render(request, 'news/post.html', context=data)
