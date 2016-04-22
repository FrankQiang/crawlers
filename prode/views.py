import requests
from pyquery import PyQuery as pq
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status
from prode.models import Goods
from prode.serializers import GoodsSerializer

class GoodsList(APIView):

    def get_source(self, source, keywords):
        data = {
            'amazon': 'http://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=',
        }
        return data[source]+keywords

    def get(self, request, format=None):
        keywords = request.query_params['keywords']
        source = 'amazon'
        url = self.get_source(source, keywords)
        req = requests.get(url)
        html = pq(req.text)
        goods_div = html.attr('id', 'atfResults')
        goods_lis = goods_div('li').html()
        data = {}
        data['html'] = goods_lis
        data['url'] = url
        return Response(data)
