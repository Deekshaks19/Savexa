import os
import sys
import django
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aidlens.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

client = Client()

# Path to an image included in the repo
img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'injury_uploads', 'Screenshot_2026-05-22_102535.png')
if not os.path.exists(img_path):
    print('Image not found:', img_path)
    sys.exit(1)

with open(img_path, 'rb') as f:
    img_data = f.read()

uploaded = SimpleUploadedFile(os.path.basename(img_path), img_data, content_type='image/png')

resp = client.post('/api/detect/', {'image': uploaded}, format='multipart')

print('status_code:', resp.status_code)
try:
    print(json.dumps(resp.json(), indent=2))
except Exception:
    print('Response content:', resp.content)
