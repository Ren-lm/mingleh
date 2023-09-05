from rest_framework import serializers
from .models import CustomUser


# UserSerializer is responsible for converting CustomUser instances to JSON and vice versa.

# It inherits from ModelSerializer, which automatically provides serialization methods 
# for easily converting between querysets and model instances, and valid JSON.

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser  # The model this serializer works with
        fields = '__all__'  # Indicates that all fields in the model should be serialized
