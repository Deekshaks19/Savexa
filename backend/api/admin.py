from django.contrib import admin
from .models import InjuryDetection, FirstAidGuidance


@admin.register(InjuryDetection)
class InjuryDetectionAdmin(admin.ModelAdmin):
    list_display = ['injury_type', 'region', 'severity', 'confidence', 'detected_at']
    list_filter = ['severity', 'injury_type', 'detected_at']
    search_fields = ['injury_type', 'region']
    readonly_fields = ['detected_at']


@admin.register(FirstAidGuidance)
class FirstAidGuidanceAdmin(admin.ModelAdmin):
    list_display = ['injury_type']
    search_fields = ['injury_type']
