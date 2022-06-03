from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
from django.utils import timezone


def index(request):
    return HttpResponse('<h1>Hello world!</h1>')


def test(request):
    return HttpResponse('Test here!')


def show(request):
    raise Exception


def time(request):
    return render(request, 'news/test.html', context={'date': timezone.now()})