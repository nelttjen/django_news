import os.path

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import ObjectDoesNotExist

from .models import ExtendedUser


# Create your views here.
@login_required
def def_profile(request):
    try:
        e_user = ExtendedUser.objects.get(user_id=request.user.id)
    except ObjectDoesNotExist:
        e_user = ExtendedUser.objects.create(user=request.user)
    data = {
        'has_image': os.path.exists(f'/static/user_profile/img/{request.user.id}.png'),
        'e_user': e_user,
    }
    return render(request, 'user_profile/profile_base.html', context=data)