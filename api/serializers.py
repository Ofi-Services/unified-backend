from rest_framework import serializers
from .models import Case, Activity, Variant, Inventory, OrderItem

class CaseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Case model.

    This serializer converts Case instances to native Python datatypes
    that can be easily rendered into JSON, XML or other content types.

    Meta:
        model (Case): The model to be serialized.
        fields (str): All fields of the model.
    """
    class Meta:
        model = Case
        fields = '__all__'

class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for the Activity model.

    This serializer converts Activity instances to native Python datatypes
    that can be easily rendered into JSON, XML or other content types.

    Meta:
        model (Activity): The model to be serialized.
        fields (list): The fields of the model to be serialized.
    """
    class Meta:
        model = Activity
        fields =  '__all__'	

class VariantSerializer(serializers.ModelSerializer):
    """
    Serializer for the Variant model.
    This serializer converts Variant model instances into JSON format and vice versa.
    It includes the following fields:
    - id: The unique identifier for the variant.
    - activities: The activities associated with the variant.
    - cases: The cases related to the variant.
    - number_cases: The number of cases for the variant.
    - percentage: The percentage representation of the variant.
    - avg_time: The average time associated with the variant.
    """

    class Meta:
        model = Variant
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Inventory model.
    This serializer converts Inventory model instances into JSON format and vice versa.
    It includes the following fields:
    - id: The unique identifier for the inventory item.
    - product_code: The code identifying the product.
    - product_name: The name of the product.
    - current_stock: The current stock level of the product.
    - unit_price: The price per unit of the product.
    """
    class Meta:
        model = Inventory
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model.
    This serializer converts OrderItem model instances into JSON format and vice versa.
    It includes the following fields:
    - id: The unique identifier for the order item.
    - order: The order associated with the order item.
    - material: The material associated with the order item.
    - quantity: The quantity of the material in the order item.
    - unit_price: The unit price of the material in the order item.
    - total_price: The total price of the order item.
    - suggestion: The suggested inventory item for the order item.
    - confidence: The confidence level of the suggestion.
    """
    class Meta:
        model = OrderItem
        fields = '__all__'