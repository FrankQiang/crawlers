import requests
from pyquery import PyQuery as pq
from rest_framework.views import APIView
from rest_framework.response import Response
from prode.models import Goods
from flash import constant


class GoodsList(APIView):

    def get_url(self, keywords, page, source):
        amazon_url = constant.AMAZON_URL.format(page=page, keywords=keywords)
        data = {
            'amazon': amazon_url,
        }
        return data[source]

    def valid_price(self, price):
        total = 1
        for currency in constant.CURRENCY:
            total *= price.find(currency)
        if total == 0:
            return True
        else:
            return False

    def get_amazon_data(self, data, html):
        goods_div = html('#atfResults')
        if not goods_div:
            return data
        i = 0
        for goods_li_data in goods_div('li'):
            goods_li = pq(pq(goods_li_data).html())
            goods_data = pq(
                pq(goods_li('.a-fixed-left-grid-inner')).html()
            )
            if goods_data:
                data['results'][i] = {}
                goods_img = pq(pq(goods_data('.a-col-left')).html())
                goods_url = pq(goods_img('a')).attr('href')
                goods_small_img_url = pq(goods_img('img')).attr('src')

                goods_info = pq(pq(goods_data('.a-col-right')).html())
                goods_title = goods_info('h2').text()
                goods_price = 0
                goods_price_div = pq(goods_info('.a-span7').html())
                goods_price_divs = goods_price_div('.a-row')
                for goods_price_div_space in goods_price_divs:
                    goods_price_div_a = pq(pq(goods_price_div_space).html())
                    goods_price = goods_price_div_a('a').text()
                    if self.valid_price(goods_price):
                        data['results'][i]['goods_price'] = goods_price
                        break
                    else:
                        data['results'][i]['goods_price'] = 0.00

                goods_des_div = pq(goods_info('.a-span5').html())
                goods_des = pq(
                    goods_des_div('.a-text-bold').nextAll()
                ).text()

                goods_large_img_url = goods_small_img_url.replace(
                    '_AC_US160_', '_SX425_'
                )
                data['results'][i]['local_url'] = constant.SINGLE_URL+goods_url
                if len(goods_url.split('.com/')) > 1:
                    data['results'][i]['url'] = goods_url.split('.com/')[1]
                data['results'][i]['goods_s_img_url'] = goods_small_img_url
                data['results'][i]['goods_l_img_url'] = goods_large_img_url
                data['results'][i]['goods_title'] = goods_title
                data['results'][i]['goods_des'] = goods_des
                i += 1
        goods_page_div = html('#bottomBar')
        goods_pages = []
        goods_cur_page = int(
            pq(pq(goods_page_div('.pagnCur')).html()).text()
        )

        goods_pages.append(goods_cur_page)
        data['cur_page'] = [goods_cur_page]

        for goods_page_data in goods_page_div('.pagnLink'):
            goods_page = int(pq(pq(goods_page_data).html()).text())
            goods_pages.append(goods_page)

        goods_last_page = pq(
            pq(goods_page_div('.pagnDisabled')).html()
        ).text()
        if goods_last_page:
            goods_pages.append(int(goods_last_page))
        data['pages'] = sorted(goods_pages)
        return data

    def get_data(self, url, source):
        r = requests.get(url)
        data = {}
        if r.status_code == 200:
            data['results'] = {}
            html = pq(r.text)
            if source == 'amazon':
                data = self.get_amazon_data(data, html)
            return data
        else:
            return data

    def get(self, request, format=None):
        if request.GET.get('page'):
            page = request.GET.get('page')
        else:
            page = 1

        if request.GET.get('source'):
            source = request.GET.get('source')
        else:
            source = 'amazon'

        if request.GET.get('keywords'):
            keywords = request.GET.get('keywords').encode('utf8')
        else:
            keywords = 'iphone'

        url = self.get_url(keywords, page, source)

        data = {}
        for time in range(constant.REQUEST_TIMES):
            if data:
                break
            else:
                data = self.get_data(url, source)

        return Response(data)


class Single(APIView):

    def get_amazon_data(self, data, html):
        goods_left_col = html('#leftCol')
        if goods_left_col:
            goods_center_col = html('#centerCol')
            goods_img_div = pq(
                pq(goods_left_col('#main-image-container')).html()
            )
            goods_img_url = pq(goods_img_div('img:first')).attr('src')
            goods_title = pq(goods_img_div('img:first')).attr('alt')
            goods_price = pq(
                pq(goods_center_col('#priceblock_ourprice')).html()
            ).text()
            data['goods_price'] = goods_price
            data['goods_title'] = goods_title
            data['goods_img_url'] = goods_img_url
        return data

    def get_data(self, url, source):
        r = requests.get(url)
        data = {}
        if r.status_code == 200:
            html = pq(r.text)
            if source == 'amazon':
                data = self.get_amazon_data(data, html)
            return data
        else:
            return data

    def get(self, request, format=None):
        if request.GET.get('url'):
            url = request.GET.get('url')
        else:
            return Response({})

        if request.GET.get('source'):
            source = request.GET.get('source')
        else:
            source = 'amazon'

        data = {}
        for time in range(constant.REQUEST_TIMES):
            if data:
                break
            else:
                data = self.get_data(url, source)
        if data:
            goods = Goods(
                title=data['goods_title'],
                price=data['goods_price'],
                image_link=data['goods_img_url']
            )
            goods.save()
        url_data = {'url': url}
        return Response(url_data)


class Index(APIView):

    def get_amazon_index_data(self, data, html):
        center_div = html('#zg_centerListWrapper')
        i = 0
        if center_div:
            goods_divs = center_div('.zg_itemImmersion')
            for goods_div in goods_divs:
                goods_div_data = pq(pq(goods_div).html())
                goods_img_div = pq(pq(goods_div_data('.zg_image')).html())
                goods_url = pq(goods_img_div('a')).attr('href')
                goods_url = goods_url.replace('\n', '')

                goods_img_url = pq(goods_img_div('img')).attr('src')

                goods_title_div = pq(pq(goods_div_data('.zg_title')).html())
                goods_title = goods_title_div.text()

                goods_price_div = pq(pq(goods_div_data('.price')).html())
                goods_price = goods_price_div.text()
                data['results'][i] = {}
                data['results'][i]['goods_title'] = goods_title
                data['results'][i]['goods_price'] = goods_price
                data['results'][i]['goods_url'] = goods_url
                data['results'][i]['goods_img_url'] = goods_img_url
                if len(goods_url.split('.com/')) > 1:
                    data['results'][i]['url'] = goods_url.split('.com/')[1]
                i += 1
        return data

    def get_data(self, url, source):
        r = requests.get(url)
        data = {}
        if r.status_code == 200:
            data['results'] = {}
            html = pq(r.text)
            if source == 'amazon':
                data = self.get_amazon_index_data(data, html)
            return data
        else:
            return data

    def get(self, request, format=None):
        if request.GET.get('source'):
            source = request.GET.get('source')
        else:
            source = 'amazon'

        data = {}
        for time in range(constant.REQUEST_TIMES):
            if data:
                break
            else:
                data = self.get_data(constant.AMAZON_INDEX, source)
        return Response(data)
