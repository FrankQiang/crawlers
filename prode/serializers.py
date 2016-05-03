from prode.models import Goods, PriceHistory
from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework_mongoengine.serializers import EmbeddedDocumentSerializer


class PriceHistorySerializer(EmbeddedDocumentSerializer):
    class Meta:
        model = PriceHistory


class GoodsSerializer(DocumentSerializer):
    price_history = PriceHistorySerializer(many=True)

    class Meta:
        model = Goods
        fields = (
            'title',
            'price',
            'brand',
            'description',
            'price_history',
        )
