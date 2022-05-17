from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect as redirect

# Create your views here.


def to_login(request):
    return redirect('/auth/login')


def login(request):
    if request.method == 'POST':
        return redirect('/news/profile')

    return render(request, 'authorize/login.html')