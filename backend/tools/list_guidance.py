import os
import sys
import django
import json
# Ensure project root (backend) is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aidlens.settings')
django.setup()
from api.models import FirstAidGuidance
rows = list(FirstAidGuidance.objects.values('id', 'injury_type'))
print(json.dumps(rows, indent=2))
