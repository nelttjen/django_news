import datetime
import os
import uuid

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.http import HttpResponseRedirect as redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from .forms import PostForm, TagSelectionForm, SearchForm
from .models import Post, Tag, Like, PageToken, Read

# global vars
LATEST_MAX_POSTS = 8
LIKED_MAX_POSTS = 8
MAIN_MAX_POSTS = 25
AJAX_MAX_POSTS = 25


# not view defs
def get_tag_link(form, match=False):
    match = "&match=1" if match else ''
    return f'filter={",".join(map(str, form.cleaned_data.get("categories")))}{match}'


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_user_by_token(token):
    token_obj = PageToken.objects.filter(token=token).first()
    if not token_obj:
        return False
    return token_obj.user

def check_user_token_valid(token):
    token_obj = PageToken.objects.filter(token=token).first()
    if not token_obj:
        return False
    return token_obj.expired > timezone.now()


def user_token(user):
    _prev = PageToken.objects.filter(user=user).first()
    if _prev:
        if not check_user_token_valid(_prev):
            _prev.delete()
        else:
            return _prev
    return PageToken.objects.create(
        token=uuid.uuid4().hex,
        user=user,
        expired=timezone.now() + datetime.timedelta(days=1)
    )


def get_posts_for_user(user):
    now = timezone.now()
    days_30 = now - datetime.timedelta(days=30)
    return Post.objects.filter(
        is_posted=True
    ).filter(
        creation_date__range=[days_30, now]
    ).all()


# ajax defs
def ajax_load_more_news(request):
    try:
        assert is_ajax(request)
        assert all(key in request.GET.keys() for key in ['post_id', 'user_id'])
        user = User.objects.get(pk=request.GET.get('user_id'))
        posts = get_posts_for_user(user)
        post_index = list(posts).index(Post.objects.get(pk=request.GET.get('post_id')))
        posts = posts[post_index + 1:post_index + AJAX_MAX_POSTS + 1]
        data = []
        for post in posts:
            item = {
                'id': post.id,
                'title': post.title,
                'content': post.content,
            }
            data.append(item)
        return JsonResponse({'data': data})
    except AssertionError:
        return HttpResponseForbidden()


@csrf_exempt
def ajax_like(request):
    try:
        assert is_ajax(request)
        token = request.POST.get('token')
        post_id = request.POST.get('post_id')
        method = request.POST.get('method')
        assert all([i is not None for i in [token, post_id, method]])
        assert method in ['add', 'remove']
        assert check_user_token_valid(token)

        user = get_user_by_token(token)
        post = Post.objects.get(pk=post_id)
        if method == 'add':
            if not Like.objects.filter(post=post).filter(user=user).first():
                Like.objects.create(
                    post=post,
                    user=user
                )
        elif method == 'remove':
            _prev = Like.objects.filter(post=post).filter(user=user).first()
            if _prev:
                _prev.delete()

        likes = len(post.like_set.all())
        return JsonResponse({
            'message': 'OK',
            'likes': likes
        })
    except (AssertionError, ObjectDoesNotExist):
        return HttpResponseForbidden()



# debug
def show(request):
    raise Exception


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
        'token': token.token,
    }
    return render(request, 'news/main_posts.html', context=data)


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
