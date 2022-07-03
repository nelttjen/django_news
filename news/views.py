from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect as redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import TemporaryUploadedFile

from .forms import PostForm
from .models import Post


# debug stuff
def test(request):
    return HttpResponse('Test here!')


def show(request):
    raise Exception


def time(request):
    return render(request, 'news/test.html', context={'date': timezone.now()})


# views
def index(request):
    return HttpResponse('<a href="new_post">Hello world!</a>')


@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).all()

    data = {
        'posts': posts
    }

    return render(request, 'news/my_posts.html', context=data)


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
                    return redirect('/profile')
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