from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from .forms import PostForm


# debug stuff
def test(request):
    return HttpResponse('Test here!')


def show(request):
    raise Exception


def time(request):
    return render(request, 'news/test.html', context={'date': timezone.now()})


# views
def index(request):
    return HttpResponse('<h1>Hello world!</h1>')


def new_post(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST)

    data = {
        'form': form,
    }
    return render(request, 'news/post.html', context=data)