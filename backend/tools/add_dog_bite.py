#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aidlens.settings')
django.setup()

from api.models import FirstAidGuidance

# Add Dog Bite guidance
dog_bite = {
    'injury_type': 'Dog Bite',
    'summary': 'Puncture or laceration from dog bite. High risk of infection and rabies.',
    'steps': [
        {'t': 'Wash thoroughly', 'd': 'Wash with soap and water for 5-10 minutes.', 'x': 'Remove any saliva or dirt.'},
        {'t': 'Apply pressure', 'd': 'If bleeding, apply clean cloth and press firmly for 5 minutes.', 'x': 'Control bleeding to prevent infection.'},
        {'t': 'Disinfect', 'd': 'Use hydrogen peroxide or antiseptic solution.', 'x': 'Kill bacteria and virus.'},
        {'t': 'Bandage', 'd': 'Cover with sterile gauze and wrap securely.', 'x': 'Prevent dirt and bacteria entry.'},
        {'t': 'Seek medical help', 'd': 'Go to hospital for rabies vaccination and tetanus shot.', 'x': 'Critical - may need antibiotics and vaccines.'}
    ]
}

FirstAidGuidance.objects.update_or_create(
    injury_type='Dog Bite',
    defaults={
        'summary': dog_bite['summary'],
        'steps': dog_bite['steps']
    }
)

print('✓ Dog Bite added to database')
print(f'Total injuries: {FirstAidGuidance.objects.count()}')
