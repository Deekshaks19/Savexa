import os
import sys
import django
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aidlens.settings')
django.setup()
from api.models import FirstAidGuidance

# Find duplicates by case-insensitive injury_type
from django.db.models import Func, Value, CharField

# Delete entries where injury_type is lowercase 'cut' but keep 'Cut'
dups = FirstAidGuidance.objects.filter(injury_type__iexact='cut').exclude(injury_type='Cut')
count = dups.count()
if count:
    print(f"Deleting {count} duplicate(s):", list(dups.values('id','injury_type')))
    dups.delete()
else:
    print('No duplicates found to delete for cut')
