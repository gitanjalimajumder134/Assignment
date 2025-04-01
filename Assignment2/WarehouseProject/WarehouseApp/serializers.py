from rest_framework import serializers
from .models import Item, PurchaseDetail, PurchaseHeader, Sell, SellDetail

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class PurchaseHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseHeader
        fields = '__all__'    

class PurchaseDetailSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    item_code = serializers.CharField(write_only=True)

    class Meta:
        model = PurchaseDetail
        fields = ['id', 'item', 'item_code', 'quantity', 'unit_price', 'header']

    def create(self, validated_data):
        """Override create to update item stock and balance"""
        item_code = validated_data.pop('item_code')
        try:
            item = Item.objects.get(code=item_code)
        except Item.DoesNotExist:
            raise serializers.ValidationError({"error": "Item not found"})

        purchase_detail = PurchaseDetail.objects.create(item=item, **validated_data)

        # Update stock & balance
        item.stock += purchase_detail.quantity
        item.balance += purchase_detail.quantity * purchase_detail.unit_price
        item.save()

        return purchase_detail
    

class SellDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellDetail
        fields = '__all__'

class SellSerializer(serializers.ModelSerializer):
    sell_details = SellDetailSerializer(many=True, read_only=True)
    class Meta:
        model = Sell
        fields = '__all__'            