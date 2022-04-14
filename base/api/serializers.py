from rest_framework.serializers import ModelSerializer
from base.models import Room

#This serializer converts an Python object to JSON object. It is more like a Form.

class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'