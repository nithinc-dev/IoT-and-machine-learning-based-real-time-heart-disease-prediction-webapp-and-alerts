from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
from .models import *
class ECGReadingSerializer(serializers.Serializer):
    ecg_data = serializers.FloatField()
    timestamp = serializers.IntegerField()  # Milliseconds since epoch

from django.utils import timezone
from datetime import datetime

class ECGBulkSerializer(serializers.Serializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    ecg_readings = ECGReadingSerializer(many=True)

    def create(self, validated_data):
        patient = validated_data['patient']
        ecg_readings = validated_data['ecg_readings']
        
        # Use timezone.now() or specify timezone correctly
        ecg_objects = [
            ECG(
                patient=patient,
                ecg_data=reading['ecg_data'],
                timestamp=datetime.fromtimestamp(
                    reading['timestamp'] / 1000.0, 
                    tz=timezone.get_current_timezone()  # Use this instead of timezone.utc
                )
            ) for reading in ecg_readings
        ]
        
        ECG.objects.bulk_create(ecg_objects)
        
        return validated_data


# class ECGBulkSerializer(serializers.Serializer):
#     patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
#     ecg_readings = ECGReadingSerializer(many=True)

#     def create(self, validated_data):
#         patient = validated_data['patient']
#         ecg_readings = validated_data['ecg_readings']
        
#         # Bulk create ECG objects with precise timestamp
#         ecg_objects = [
#             ECG(
#                 patient=patient,
#                 ecg_data=reading['ecg_data'],
#                 timestamp=datetime.fromtimestamp(
#                     reading['timestamp'] / 1000.0, 
#                     tz=timezone.utc
#                 )
#             ) for reading in ecg_readings
#         ]
        
#         # Use bulk_create for efficiency
#         ECG.objects.bulk_create(ecg_objects)
        
#         return validated_data



from rest_framework import serializers
from .models import Location

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['latitude', 'longitude', 'altitude', 'timestamp']








# from rest_framework import serializers
# from .models import ECG, Patient
# from django.utils import timezone

# class ECGReadingSerializer(serializers.Serializer):
#     ecg_data = serializers.FloatField()
#     timestamp = serializers.IntegerField()  # Milliseconds since epoch

# class ECGBulkSerializer(serializers.Serializer):
#     patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
#     ecg_readings = ECGReadingSerializer(many=True)

#     def create(self, validated_data):
#         patient = validated_data['patient']
#         ecg_readings = validated_data['ecg_readings']
        
#         # Bulk create ECG objects
#         ecg_objects = [
#             ECG(
#                 patient=patient,
#                 ecg_data=reading['ecg_data'],
#                 timestamp=timezone.datetime.fromtimestamp(reading['timestamp']/1000.0, tz=timezone.utc)
#             ) for reading in ecg_readings
#         ]
        
#         # Use bulk_create for efficiency
#         ECG.objects.bulk_create(ecg_objects)
        
#         return validated_data

# from rest_framework import serializers
# from .models import ECG

# class ECGSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ECG
#         fields = ['patient', 'ecg_data', 'timestamp']
