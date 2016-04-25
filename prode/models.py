from __future__ import unicode_literals

from mongoengine import *

class Goods(Document):
    title = StringField(max_length=1024)
    price = StringField(max_length=100)
    image_link = StringField(max_length=1024)
    pub_date = DateTimeField(help_text='date stored')
