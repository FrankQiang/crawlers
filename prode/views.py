import requests
from pyquery import PyQuery as pq
from mongoengine import NotUniqueError
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.core.paginator import Paginator
from prode.models import Goods, Sku, Specs
from flash import constant
from prode.serializers import GoodsSerializer


class GoodsList(APIView):

    def get_url(self, keywords, page, brand, sort, source):
        if source == 'amazon_us':
            url = constant.AMAZON_URL_US.format(
                page=page,
                keywords=keywords,
                sort=sort,
                brand=brand
            )
        elif source == 'amazon_uk':
            url = constant.AMAZON_URL_UK.format(
                page=page,
                keywords=keywords,
                sort=sort,
                brand=brand
            )
        else:
            url = constant.AMAZON_HOST_US
        return url

    def valid_price(self, price):
        total = 1
        for currency in constant.CURRENCY:
            total *= price.find(currency)
        if total == 0:
            return True
        else:
            return False

    def get_amazon_data(self, data, html, source):
        i = 0
        goods_ul = html('#s-results-list-atf')
        if not goods_ul:
            return data
        goods_li_first = goods_ul('li:first')
        goods_li_first_num = int(goods_li_first.attr('id').split('_')[1])
        goods_li_last_num = goods_li_first_num + 20
        for result_num in range(goods_li_first_num, goods_li_last_num):
            goods_li = pq(html('#result_'+str(result_num)))
            if goods_li:
                data['results'][i] = {}
                goods_img = pq(goods_li('img'))
                goods_a = pq(goods_li('img').parents('a'))
                goods_url = pq(goods_a('a')).attr('href')
                goods_small_img_url = pq(goods_img('img')).attr('src')

                goods_title = goods_li('h2').attr('data-attribute')
                goods_price = 0
                goods_price_spans = pq(goods_li('.a-color-price').html())
                for goods_price_span in goods_price_spans:
                    goods_price = pq(goods_price_span).text()
                    if self.valid_price(goods_price):
                        data['results'][i]['goods_price'] = goods_price
                        continue
                    else:
                        data['results'][i]['goods_price'] = 0.00

                goods_des = goods_li('em').parents('span').text()

                goods_large_img_url = goods_small_img_url.replace(
                    constant.AMAZON_iMG_SMA_SIZE, constant.AMAZON_iMG_MED_SIZE
                )
                data['results'][i]['local_url'] = constant.SINGLE_URL.format(
                    url=goods_url,
                    source=source,
                )
                if goods_url.find('.com/') > 0:
                    data['results'][i]['url'] = goods_url.split('.com/')[1]
                elif goods_url.find('.co.uk/') > 0:
                    data['results'][i]['url'] = goods_url.split('.co.uk/')[1]
                else:
                    data['results'].pop(i)
                    continue

                data['results'][i]['goods_s_img_url'] = goods_small_img_url
                data['results'][i]['goods_l_img_url'] = goods_large_img_url
                data['results'][i]['goods_title'] = goods_title
                data['results'][i]['goods_des'] = goods_des
                i += 1
        data['brand'] = []
        brands = pq(html('#ref_2528832011'))
        if not brands:
            brands = pq(html('#ref_1632651031'))
        for brand in brands('li'):
            brand = pq(brand)
            if brand('.refinementImage'):
                data['brand'].append(brand.text())
        goods_page_div = html('#bottomBar')
        goods_pages = []

        goods_cur_page = pq(pq(goods_page_div('.pagnCur')).html()).text()
        if goods_cur_page:
            goods_cur_page = int(goods_cur_page)

        goods_pages.append(goods_cur_page)
        data['cur_page'] = [goods_cur_page]

        for goods_page_data in goods_page_div('.pagnLink'):
            goods_page = pq(pq(goods_page_data).html()).text()
            if goods_page:
                goods_page = int(goods_page)
            goods_pages.append(goods_page)

        goods_last_page = pq(
            pq(goods_page_div('.pagnDisabled')).html()
        ).text()
        if goods_last_page:
            goods_pages.append(int(goods_last_page))
        data['pages'] = sorted(goods_pages)
        return data

    def get_data(self, url, source):
        data = {}
        if source == 'amazon_us':
            r = requests.get(url, headers=constant.AMAZON_HEADERS_US)
            if r.status_code == 200:
                data['results'] = {}
                html = pq(r.text)
                data = self.get_amazon_data(data, html, source)
                return data
            else:
                return data
        elif source == 'amazon_uk':
            r = requests.get(url, headers=constant.AMAZON_HEADERS_UK)
            if r.status_code == 200:
                data['results'] = {}
                html = pq(r.text)
                data = self.get_amazon_data(data, html, source)
                return data
            else:
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
            source = 'amazon_us'

        if request.GET.get('keywords'):
            keywords = request.GET.get('keywords')
        else:
            keywords = 'iphone'

        if request.GET.get('sort'):
            sort = request.GET.get('sort')
        else:
            sort = ''

        if request.GET.get('brand'):
            brand = request.GET.get('brand')
        else:
            brand = ''

        url = self.get_url(keywords, page, brand, sort, source)

        data = {}
        for time in range(constant.REQUEST_TIMES):
            if data:
                break
            else:
                data = self.get_data(url, source)

        return Response(data)


class Single(APIView):

    def get_amazon_data(self, data, html):
        nav = pq(html('#nav-subnav'))
        goods_left_col = html('#leftCol')
        # goods_center_col = html('#centerCol')
        goods_type = pq(nav('a:first')).text()

        goods_img_div = pq(
            pq(goods_left_col('#altImages')).html()
        )
        goods_imgs = goods_img_div('img')
        data['goods_imgs'] = []
        for goods_img in goods_imgs:
            goods_img_url = pq(goods_img).attr('src').replace(
                constant.AMAZON_iMG_MIN_SIZE, constant.AMAZON_iMG_MED_SIZE
            )
            data['goods_imgs'].append(goods_img_url)

        goods_title = pq(html('#title')).text()
        goods_brand = pq(html('#brand')).text()
        goods_price = html('#priceblock_ourprice').text()
        if not goods_price:
            goods_price = html('#priceblock_saleprice').text()

        data['goods_title'] = goods_title
        data['goods_type'] = goods_type
        data['goods_price'] = goods_price
        data['goods_brand'] = goods_brand
        if len(data['goods_imgs']) > 1:
            data['goods_img_url'] = data['goods_imgs'][0]
        else:
            data['goods_img_url'] = ''

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
        goods_params = pq(html('#productDetails_detailBullets_sections1'))
        if goods_params:
            data['params'] = []
            goods_params_trs = pq(goods_params('tr'))
            for goods_params_tr in goods_params_trs:
                param = []
                goods_params_tr = pq(goods_params_tr)
                goods_params_th = goods_params_tr('th').text()
                goods_params_td = goods_params_tr('td').text()
                if len(goods_params_td) > constant.STR_LEN:
                    continue
                param.append(goods_params_th)
                param.append(goods_params_td)
                data['params'].append(param)

        return data

    def get_data(self, url, source):
        data = {}
        if source == 'amazon_us':
            r = requests.get(url, headers=constant.AMAZON_HEADERS_US)
            if r.status_code == 200:
                data['results'] = {}
                html = pq(r.text)
                data['id'] = url.split('/ref')[0].split('/')[-1]
                data = self.get_amazon_data(data, html)
                return data
            else:
                return data
        elif source == 'amazon_uk':
            r = requests.get(url, headers=constant.AMAZON_HEADERS_UK)
            if r.status_code == 200:
                data['results'] = {}
                html = pq(r.text)
                data['id'] = url.split('/ref')[0].split('/')[-1]
                data = self.get_amazon_data(data, html)
                return data
            else:
                return data
        else:
            return data

    def get(self, request, format=None):
        if request.GET.get('url'):
            url = request.GET.get('url')
        else:
            content = {'mes': 'Not url'}
            return Response(status.HTTP_400_BAD_REQUEST)

        if request.GET.get('source'):
            source = request.GET.get('source')
        else:
            source = 'amazon_us'

        data = {}
        for time in range(constant.REQUEST_TIMES):
            if data:
                break
            else:
                data = self.get_data(url, source)
        if not data.get('goods_price') and data.get('sku'):
            data['goods_price'] = data['sku'][0]['price']

        if data and data.get('goods_price'):
            goods = Goods(
                source=source,
                goods_id=data['id'],
                goods_url=url,
                title=data['goods_title'],
                goods_type=data['goods_type'],
                price=data['goods_price'],
                image_link=data['goods_img_url'],
                brand=data['goods_brand'],
                images=data['goods_imgs']
            )
            if data.get('sku'):
                for sku_data in data['sku']:
                    sku = Sku(
                        union_type=sku_data['union_type'],
                        price=sku_data['price']
                    )
                    goods.sku.append(sku)

            if data.get('params'):
                for param in data['params']:
                    specs = Specs(params_title=param[0], params_con=param[1])
                    goods.specs.append(specs)
            try:
                goods.save()
                content = {'url': url}
                re_status = status.HTTP_200_OK
            except NotUniqueError:
                content = {'mes': 'Goods alread exist'}
                re_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            content = {'mes': 'Get data error'}
            re_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(content, status=re_status)


class Index(APIView):

    def get_amazon_data(self, data, html):
        right_div = html('#zg_col2')
        i = 0
        if right_div:
            goods_divs = right_div('.zg_more_item')
            for goods_div in goods_divs:
                goods_div = pq(goods_div)
                goods_url = goods_div('a').attr('href')
                goods_url = goods_url.replace('\n', '')
                goods_img_url = goods_div('img').attr('src')
                goods_img_url = goods_img_url.replace(
                    constant.AMAZON_iMG_SSS_SIZE, constant.AMAZON_iMG_SMS_SIZE)
                goods_title = goods_div('a').attr('title')
                goods_price = pq(goods_div('.zg_morePrice')).text()
                data['results'][i] = {}
                data['results'][i]['goods_title'] = goods_title
                data['results'][i]['goods_price'] = goods_price
                data['results'][i]['local_url'] = constant.SINGLE_URL+goods_url
                data['results'][i]['goods_img_url'] = goods_img_url
                if len(goods_url.split('.com/')) > 1:
                    data['results'][i]['url'] = goods_url.split('.com/')[1]
                i += 1
        return data

    def get_data(self, url, source):
        data = {}
        if source == 'amazon_us':
            r = requests.get(url, headers=constant.AMAZON_HEADERS_US)
            if r.status_code == 200:
                data['results'] = {}
                html = pq(r.text)
                data = self.get_amazon_data(data, html)
                return data
            else:
                return data
        elif source == 'amazon_uk':
            r = requests.get(url, headers=constant.AMAZON_HEADERS_UK)
            if r.status_code == 200:
                data['results'] = {}
                html = pq(r.text)
                data = self.get_amazon_data(data, html)
                return data
            else:
                return data
        else:
            return data

    def get(self, request, format=None):
        if request.GET.get('source'):
            source = request.GET.get('source')
        else:
            source = 'amazon_us'
        if source == 'amazon_uk':
            url = constant.AMAZON_INDEX_UK
        else:
            url = constant.AMAZON_INDEX_US

        data = {}
        for time in range(constant.REQUEST_TIMES):
            if data:
                break
            else:
                data = self.get_data(url, source)
        return Response(data)


class Product(APIView):

    def get(self, request, format=None):
        if request.GET.get('page'):
            page = request.GET.get('page')
        else:
            page = 1
        goods = Goods.objects.all()
        data_all = GoodsSerializer(goods, many=True).data
        page_size = constant.PAGE_SIZE
        paginator = Paginator(data_all, page_size)
        page_total = paginator.num_pages
        page_each = paginator.page(page)
        page_data = page_each.object_list
        for page_each_data in page_data:
            page_each_data['price_history'] = []
        data = {}
        data['page_total'] = [page_total]
        data['results'] = page_data
        return Response(data)


class History(APIView):

    def get(self, request, format=None):
        if request.GET.get('page'):
            page = request.GET.get('page')
        else:
            page = 1
        if request.GET.get('id'):
            id = request.GET.get('id')
            goods = Goods.objects.get(id=id)
            goods_data = GoodsSerializer(goods).data
            price_all_data = goods_data['price_history']
            page_size = constant.PAGE_SIZE
            paginator = Paginator(price_all_data, page_size)
            page_total = paginator.num_pages
            page_each = paginator.page(page)
            page_data = page_each.object_list
            data = {}
            data['page_total'] = [page_total]
            data['results'] = page_data
        else:
            data = []
        return Response(data)
