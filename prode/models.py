import datetime
from mongoengine import fields
from mongoengine import Document
from mongoengine import EmbeddedDocument


class Sku(EmbeddedDocument):
    union_type = fields.ListField(fields.StringField(max_length=50))
    price = fields.StringField(max_length=100)


class Specs(EmbeddedDocument):
    params_title = fields.StringField(max_length=100)
    params_con = fields.StringField(max_length=100)


class Offer(EmbeddedDocument):
    shop_name = fields.StringField(max_length=100)
    shop_url = fields.StringField(max_length=1024)
    name = fields.StringField(max_length=100)
    price = fields.FloatField()
    price_with_shipping = fields.FloatField()
    shipping_costs = fields.FloatField()
    currency = fields.StringField(max_length=50)
    url = fields.StringField(max_length=1024)


class PriceHistory(EmbeddedDocument):
    price = fields.StringField(max_length=100)
    pub_date = fields.DateTimeField(default=datetime.datetime.now)


class Log(Document):
    source = fields.StringField()
    request_times = fields.IntField()
    error_times = fields.IntField()
    success_times = fields.IntField()


class Goods(Document):
    source = fields.StringField(max_length=50)
    goods_id = fields.StringField(max_length=64)
    goods_url = fields.StringField(max_length=1024, unique=True)
    title = fields.StringField(max_length=1024)
    goods_type = fields.StringField(max_length=50)
    country = fields.StringField(max_length=100)
    link = fields.StringField(max_length=1024)
    mobile_link = fields.StringField(max_length=1024)
    image_link = fields.StringField(max_length=1024)
    images = fields.ListField(fields.StringField(max_length=1024))
    availability = fields.StringField(max_length=100)
    availability_date = fields.StringField(max_length=100)
    price = fields.StringField(max_length=100)
    sale_price = fields.FloatField()
    sale_price_effective_date = fields.StringField(max_length=100)
    brand = fields.StringField(max_length=100)
    material = fields.StringField(max_length=100)
    pattern = fields.StringField(max_length=100)
    shipping = fields.StringField(max_length=100)
    shipping_weight = fields.StringField(max_length=100)
    shipping_label = fields.StringField(max_length=100)
    multipack = fields.StringField(max_length=100)
    sku = fields.ListField(fields.EmbeddedDocumentField(Sku))
    specs = fields.ListField(fields.EmbeddedDocumentField(Specs))
    description = fields.StringField(max_length=1024)
    offer = fields.DateTimeField(Offer)
    price_history = fields.ListField(
        fields.EmbeddedDocumentField(PriceHistory))
    pub_date = fields.DateTimeField(default=datetime.datetime.now)
