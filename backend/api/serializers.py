from rest_framework import serializers
from .models import InjuryDetection, FirstAidGuidance


class InjuryDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InjuryDetection
        fields = ['id', 'injury_type', 'region', 'severity', 'confidence', 'image', 'detected_at']


class FirstAidGuidanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstAidGuidance
        fields = ['id', 'injury_type', 'summary', 'steps']
