from django.db import migrations


def create_guidance(apps, schema_editor):
    FirstAidGuidance = apps.get_model('api', 'FirstAidGuidance')
    guidance_data = [
        {
            'injury_type': 'Sprain',
            'summary': 'A sprain is an injury to ligaments. Use RICE method: Rest, Ice, Compression, Elevation.',
            'steps': [
                {
                    't': 'Rest the area',
                    'd': 'Stop activity and avoid putting weight on the injured joint.',
                    'x': 'Use crutches if needed to avoid weight-bearing.'
                },
                {
                    't': 'Apply ice',
                    'd': 'Ice the area for 15-20 minutes every 2-3 hours for the first 48 hours.',
                    'x': 'Wrap ice in a towel to protect skin.'
                },
                {
                    't': 'Compress',
                    'd': 'Use an elastic bandage to reduce swelling. Ensure it is snug but not too tight.',
                    'x': 'Check circulation: if toes turn pale or numb, loosen the bandage.'
                },
                {
                    't': 'Elevate',
                    'd': 'Raise the injured area above heart level when possible.',
                    'x': 'Use pillows to support elevation.'
                },
                {
                    't': 'Monitor progress',
                    'd': 'If no improvement after 48-72 hours, see a doctor.',
                    'x': 'Swelling or severe pain warrants immediate medical attention.'
                }
            ]
        },
        {
            'injury_type': 'Fracture',
            'summary': 'A fracture is a break in a bone. Immobilize immediately and seek emergency care.',
            'steps': [
                {
                    't': 'Stop activity',
                    'd': 'Do not move the injured area. Immobilize immediately.',
                    'x': 'Avoid any movement that could worsen the break.'
                },
                {
                    't': 'Apply ice',
                    'd': 'Wrap ice in cloth and apply to reduce swelling.',
                    'x': 'Do not apply ice directly to skin.'
                },
                {
                    't': 'Immobilize',
                    'd': 'Use a sling, splint, or support to prevent movement.',
                    'x': 'Keep the area as still as possible.'
                },
                {
                    't': 'Elevate if possible',
                    'd': 'Raise the injured area to reduce swelling.',
                    'x': 'Use pillows for support.'
                },
                {
                    't': 'Call 911',
                    'd': 'Seek immediate medical attention for proper diagnosis and treatment.',
                    'x': 'Do not eat or drink in case surgery is needed.'
                }
            ]
        },
        {
            'injury_type': 'Abrasion',
            'summary': 'An abrasion is a surface scrape. Clean gently and apply antibiotic ointment.',
            'steps': [
                {
                    't': 'Rinse gently',
                    'd': 'Wash with clean running water to remove dirt and debris.',
                    'x': 'Do not scrub; use gentle pressure only.'
                },
                {
                    't': 'Pat dry',
                    'd': 'Use a clean cloth to pat (not rub) the area dry.',
                    'x': 'Leave it slightly damp for ointment application.'
                },
                {
                    't': 'Apply antibiotic ointment',
                    'd': 'Spread a thin layer of antibiotic ointment to prevent infection.',
                    'x': 'Neosporin or similar products work well.'
                },
                {
                    't': 'Cover loosely',
                    'd': 'Use a non-stick bandage or gauze to protect the area.',
                    'x': 'Change dressing daily or when it becomes wet.'
                },
                {
                    't': 'Watch for infection',
                    'd': 'Monitor for redness, warmth, pus, or increased pain.',
                    'x': 'See a doctor if signs of infection appear.'
                }
            ]
        },
        {
            'injury_type': 'Bleeding',
            'summary': 'Heavy bleeding requires immediate pressure to stop blood flow. Call 911 for severe cases.',
            'steps': [
                {
                    't': 'Apply direct pressure',
                    'd': 'Press a clean cloth firmly against the wound.',
                    'x': 'Maintain steady pressure for 5-10 minutes.'
                },
                {
                    't': 'Do not remove cloth',
                    'd': 'If soaked, add more cloth on top rather than removing the first layer.',
                    'x': 'Removing cloth can disrupt clotting.'
                },
                {
                    't': 'Elevate',
                    'd': 'Raise the bleeding area above the heart if possible and safe.',
                    'x': 'This reduces blood flow to the area.'
                },
                {
                    't': 'Apply bandage',
                    'd': 'Once bleeding slows, wrap with a clean bandage to secure.',
                    'x': 'Keep pressure applied.'
                },
                {
                    't': 'Call 911 if needed',
                    'd': 'Seek emergency help if bleeding does not stop after 10 minutes.',
                    'x': 'Large wounds or arterial bleeding require immediate professional help.'
                }
            ]
        }
    ]

    for item in guidance_data:
        FirstAidGuidance.objects.update_or_create(
            injury_type=item['injury_type'],
            defaults={
                'summary': item['summary'],
                'steps': item['steps'],
            }
        )


def delete_guidance(apps, schema_editor):
    FirstAidGuidance = apps.get_model('api', 'FirstAidGuidance')
    FirstAidGuidance.objects.filter(injury_type__in=['Sprain', 'Fracture', 'Abrasion', 'Bleeding']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_seed_guidance'),
    ]

    operations = [
        migrations.RunPython(create_guidance, delete_guidance),
    ]
