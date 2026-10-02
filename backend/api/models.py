from django.db import models

class InjuryDetection(models.Model):
    """Store injury detection results"""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    injury_type = models.CharField(max_length=100)  # e.g., "Burn", "Cut"
    region = models.CharField(max_length=100)  # e.g., "Forearm", "Finger"
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    confidence = models.FloatField()  # 0-100
    image = models.ImageField(upload_to='injury_uploads/')
    detected_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.injury_type} - {self.region} ({self.severity})"
    
    class Meta:
        ordering = ['-detected_at']


class FirstAidGuidance(models.Model):
    """Store first-aid steps"""
    injury_type = models.CharField(max_length=100, unique=True)
    summary = models.TextField()
    steps = models.JSONField()  # List of steps with title, description, note
    
    def __str__(self):
        return self.injury_type
