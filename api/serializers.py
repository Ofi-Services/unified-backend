from rest_framework import serializers
from .models import Case, Activity, Variant, Bill, Rework

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
        fields =  ['id','case', 'timestamp', 'name', 'case_index', 'tpt']	

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
        fields = ['id', 'activities', 'cases', 'number_cases', 'percentage', 'avg_time']
        
class BillSerializer(serializers.ModelSerializer):
    """
    Serializer for the Bill model.

    This serializer converts Bill instances to native Python datatypes
    that can be easily rendered into JSON, XML or other content types.

    Meta:
        model (Bill): The model to be serialized.
        fields (list): The fields of the model to be serialized.
    """
    case = CaseSerializer()

    class Meta:
        model = Bill
        fields = ['id', 'case', 'timestamp', 'value']

class ReworkSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rework model.

    This serializer converts Rework instances to native Python datatypes.
    """
    activity = ActivitySerializer()
    case = serializers.SerializerMethodField()

    def get_case(self, obj):
        return CaseSerializer(obj.activity.case).data

    class Meta:
        model = Rework
        fields = ['id', 'activity', 'case', 'cost', 'target', 'cause']

