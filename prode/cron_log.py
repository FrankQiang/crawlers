import requests
import random
from pyquery import PyQuery as pq
from prode.models import Log
from flash import constant


class Amazon(object):

    def handle(self):
        probability = 0.5
        if probability > random.random():
            url = constant.AMAZON_HOST_US
            source = 'amazon_us'
        else:
            url = constant.AMAZON_HOST_UK
            source = 'amazon_uk'

        data = self.get_data(url, source)
        if data and data.get('price'):
            log = Log.objects(source=source)
            if not log:
                log = Log(
                    source=source,
                    request_times=1,
                    success_times=1
                )
            else:
                log = Log.objects.get(source=source)
                log['request_times'] += 1
                log['success_times'] += 1
            log.save()
        else:
            log = Log.objects(source=source)
            if not log:
                log = Log(
                    source=source,
                    request_times=1,
                    error_times=1
                )
            else:
                log = Log.objects.get(source=source)
                log['request_times'] += 1
                log['error_times'] += 1
            log.save()

    def get_amazon_data(self, data, html):
        goods_price = html('#priceblock_ourprice').text()
        if not goods_price:
            goods_price = html('#priceblock_saleprice').text()
        data['price'] = goods_price
        goods_twister_feature = html('#twister_feature_div')
        if goods_twister_feature:
            data['sku'] = []
            goods_size_div = pq(html('#variation_size_name'))
            goods_color_div = pq(html('#variation_color_name'))
            if goods_color_div and not goods_size_div:
                goods_color_lis = pq(goods_color_div('li'))
                for goods_color_li in goods_color_lis:
                    goods_color_li = pq(goods_color_li)
                    goods_color = goods_color_li('img').attr('alt')
                    goods_color_price = pq(
                        goods_color_li('#'+goods_color_li.attr('id')+'_price')
                    ).text()
                    sku = {}
                    sku['price'] = goods_color_price
                    sku['union_type'] = []
                    sku['union_type'].append(goods_color)
                    data['sku'].append(sku)
        if not data.get('goods_price') and data.get('sku'):
            data['goods_price'] = data['sku'][0]['price']

        return data

    def get_data(self, url, source):
        data = {}
        if source == 'amazon_us':
            r = requests.get(url, headers=constant.AMAZON_HEADERS_US)
            if r.status_code == 200:
                data['prode'] = ''
                html = pq(r.text)
                data = self.get_amazon_data(data, html)
                return data
            else:
                return data
        elif source == 'amazon_uk':
            r = requests.get(url, headers=constant.AMAZON_HEADERS_UK)
            if r.status_code == 200:
                data['prode'] = ''
                html = pq(r.text)
                data = self.get_amazon_data(data, html)
                return data
            else:
                return data
        else:
            return data


def get_connect_log():
    amazon = Amazon()
    amazon.handle()
