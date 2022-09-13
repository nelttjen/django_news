import requests
import json

from django.test import TestCase


# Create your tests here.
class AjaxTest(TestCase):
    def setUp(self) -> None:
        pass

    # @classmethod
    # def test_ajax_like(cls):
    #     headers = {'x-requested-with': 'XMLHttpRequest'}
    #     data = {
    #         'token': '3e0114b3f8064deea9cb3ccea64135cc',
    #         'post_id': 16,
    #         'method': 'add'
    #     }
    #     for i in range(3):
    #         resp = requests.request('POST', 'http://127.0.0.1:8000/news/api/like',
    #                                 data=data, headers=headers)
    #         if resp.status_code != 20:
    #             raise Test

    def test_1(self):
        print(requests.get('https://toptoon.com/latest'))