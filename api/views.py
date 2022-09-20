from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import LikesSerializer
from news.models import Like, Post
from news.util import is_ajax, check_user_token_valid, get_user_by_token


class CommentsView(APIView):
    def get(self):
        pass


class LikesView(APIView):
    def get(self, request, post_id):
        likes = Like.objects.filter(post_id=int(post_id)).all()
        msg = 'OK'
        _data = []
        if not Post.objects.filter(id=int(post_id)).first():
            msg = 'Post not found'
        else:
            _data = LikesSerializer(likes, many=True).data
        return Response({'data': _data, 'message': msg})

    def post(self, request, post_id):
        try:
            assert is_ajax(request), 'not ajax'
            token = request.POST.get('token')
            method = request.POST.get('method')
            assert all([i is not None for i in [token, post_id, method]]), "data wrong"
            assert method in ['add', 'remove'], 'method wrong'
            assert check_user_token_valid(token), 'token fail'

            user = get_user_by_token(token)
            post = Post.objects.get(pk=post_id)
            if method == 'add':
                if not Like.objects.filter(post=post).filter(user=user).exists():
                    Like.objects.create(
                        post=post,
                        user=user
                    )
            elif method == 'remove':
                _prev = Like.objects.filter(post=post).filter(user=user).first()
                if _prev:
                    _prev.delete()

            likes = LikesSerializer(post.like_set.all(), many=True)
            return Response({
                'message': 'OK',
                'likes': len(likes.data)
            })
        except (AssertionError, ObjectDoesNotExist) as e:
            print(e)
            return Response({
                'message': 'error',
                'likes': None,
            })