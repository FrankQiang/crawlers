from prode.models import Goods, PriceHistory, Sku, Specs
from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework_mongoengine.serializers import EmbeddedDocumentSerializer


class PriceHistorySerializer(EmbeddedDocumentSerializer):
    class Meta:
        model = PriceHistory


class SkuSerializer(EmbeddedDocumentSerializer):
    class Meta:
        model = Sku


class SpecsSerializer(EmbeddedDocumentSerializer):
    class Meta:
        model = Specs


class GoodsSerializer(DocumentSerializer):
    price_history = PriceHistorySerializer(many=True)
    sku = SkuSerializer(many=True)
    specs = SpecsSerializer(many=True)

    class Meta:
        model = Goods
