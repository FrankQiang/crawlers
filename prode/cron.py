import requests
from pyquery import PyQuery as pq
from prode.models import Goods, PriceHistory
from flash import constant


class Amazon(object):

    def handle(self):
        goods = Goods.objects.all()
        for per_goods in goods:
            data = {}
            for time in range(constant.REQUEST_TIMES):
                if data:
                    break
                else:
                    data = self.get_data(per_goods.goods_url, per_goods.source)
            if data and data.get('price'):
                price = PriceHistory(price=data['price'])
                per_goods.price_history.append(price)
                per_goods.save()

    def get_amazon_data(self, data, html):
        goods_price = html('#priceblock_ourprice').text()
        data['price'] = goods_price
        return data

    def get_data(self, url, source):
        r = requests.get(url)
        data = {}
        if r.status_code == 200:
            data['prode'] = ''
            html = pq(r.text)
            if source == 'amazon':
                data = self.get_amazon_data(data, html)
            return data
        else:
            return data


def get_goods_price():
    amazon = Amazon()
    amazon.handle()
