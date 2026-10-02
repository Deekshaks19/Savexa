from django.db import migrations


def create_guidance(apps, schema_editor):
    FirstAidGuidance = apps.get_model('api', 'FirstAidGuidance')
    guidance_data = [
        {
            'injury_type': 'Burn',
            'summary': 'First aid for burns focuses on cooling, protecting the area, and preventing infection.',
            'steps': [
                {
                    't': 'Cool the burn',
                    'd': 'Hold the injured area under cool running water for 10 to 15 minutes.',
                    'x': 'Avoid ice or very cold water because it can further damage the skin.'
                },
                {
                    't': 'Remove tight items',
                    'd': 'Gently remove jewelry or clothing near the burn before swelling begins.',
                    'x': 'Do not remove anything that is stuck to the skin.'
                },
                {
                    't': 'Cover the burn',
                    'd': 'Use a sterile, non-stick dressing or clean cloth to cover the area loosely.',
                    'x': 'Do not apply butter, toothpaste, or oily substances to the burn.'
                },
                {
                    't': 'Take pain relief',
                    'd': 'Use an over-the-counter pain reliever if appropriate.',
                    'x': 'Follow the dosage instructions on the label.'
                },
                {
                    't': 'Watch for infection',
                    'd': 'Check for increased redness, swelling, pus, or fever.',
                    'x': 'Seek medical help if signs of infection develop or the burn is large.'
                }
            ]
        },
        {
            'injury_type': 'Cut',
            'summary': 'First aid for cuts focuses on stopping bleeding, cleaning the wound, and protecting it from infection.',
            'steps': [
                {
                    't': 'Apply pressure',
                    'd': 'Press a clean cloth or sterile dressing firmly against the cut until bleeding slows.',
                    'x': 'Keep steady pressure and do not remove the cloth too quickly.'
                },
                {
                    't': 'Clean the wound',
                    'd': 'Rinse the cut gently with clean running water to remove debris.',
                    'x': 'Avoid using hydrogen peroxide directly on the wound as it can irritate tissue.'
                },
                {
                    't': 'Use antiseptic',
                    'd': 'Apply a thin layer of antiseptic if available to reduce infection risk.',
                    'x': 'If no antiseptic is available, keep the wound clean and dry.'
                },
                {
                    't': 'Cover and protect',
                    'd': 'Cover the cut with a sterile bandage or dressing.',
                    'x': 'Change the dressing if it becomes wet or dirty.'
                },
                {
                    't': 'Monitor healing',
                    'd': 'Watch for redness, swelling, warmth, or pus around the cut.',
                    'x': 'Seek medical care if the cut is deep, won’t stop bleeding, or shows infection.'
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
    FirstAidGuidance.objects.filter(injury_type__in=['Burn', 'Cut']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_guidance, delete_guidance),
    ]
