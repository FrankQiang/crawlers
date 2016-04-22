from prode.models import Goods
from rest_framework import serializers

class GoodsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Goods
        fields = ('title', 'price', 'fare', 'tax', 'currency', 'brand', 'description')
