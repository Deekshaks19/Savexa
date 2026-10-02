from django.db import migrations
import json


def create_additional_guidance(apps, schema_editor):
    FirstAidGuidance = apps.get_model('api', 'FirstAidGuidance')

    guidance_data = [
        {
            'injury_type': 'Scratch',
            'summary': 'Minor skin break from scraping—clean and protect.',
            'steps': [
                {'t': 'Clean the area', 'd': 'Gently wash with soap and water.', 'x': ''},
                {'t': 'Apply antiseptic', 'd': 'Use an antiseptic wipe or solution.', 'x': ''},
                {'t': 'Cover', 'd': 'Place a small sterile dressing or plaster.', 'x': ''},
                {'t': 'Keep dry', 'd': 'Change dressing if it becomes wet or dirty.', 'x': ''},
                {'t': 'Watch for infection', 'd': 'Seek care if redness or pus appears.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Rash',
            'summary': 'Skin irritation causing redness and itching.',
            'steps': [
                {'t': 'Stop exposures', 'd': 'Remove any new soap, cream or clothing causing rash.', 'x': ''},
                {'t': 'Cool the skin', 'd': 'Use cool compresses to reduce itching.', 'x': ''},
                {'t': 'Apply topical', 'd': 'Use hydrocortisone or calamine for mild rashes.', 'x': 'Avoid strong steroids unless advised.'},
                {'t': 'Antihistamine', 'd': 'Oral antihistamines may reduce itch.', 'x': ''},
                {'t': 'See clinician', 'd': 'If widespread, painful, or with systemic symptoms, seek medical care.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Animal Bite',
            'summary': 'Bites from animals can introduce infection—clean and seek advice.',
            'steps': [
                {'t': 'Stop bleeding', 'd': 'Apply firm pressure with a clean cloth.', 'x': ''},
                {'t': 'Clean wound', 'd': 'Rinse with water and mild soap.', 'x': ''},
                {'t': 'Cover', 'd': 'Apply sterile dressing and seek medical review.', 'x': 'Bites to hands and face need prompt care.'},
                {'t': 'Tetanus/rabies', 'd': 'Consider tetanus or rabies risk — get medical advice.', 'x': ''},
                {'t': 'Watch for infection', 'd': 'Return if increasing redness, swelling or fever.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Bee Sting',
            'summary': 'Local pain, swelling, and sometimes allergic reactions.',
            'steps': [
                {'t': 'Remove stinger', 'd': 'Scrape out stinger with fingernail or card.', 'x': 'Do not pinch — that may inject more venom.'},
                {'t': 'Cool', 'd': 'Apply ice pack wrapped in cloth to reduce swelling.', 'x': ''},
                {'t': 'Antihistamine', 'd': 'Take oral antihistamine for itching.', 'x': ''},
                {'t': 'Monitor', 'd': 'Watch for breathing difficulty or widespread swelling.', 'x': 'If present, call emergency services.'},
                {'t': 'Pain relief', 'd': 'Use paracetamol or ibuprofen as needed.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Cat Bite',
            'summary': 'Cat bites cause deep punctures and high infection risk; seek medical care.',
            'steps': [
                {'t': 'Clean thoroughly', 'd': 'Irrigate with clean water for several minutes.', 'x': ''},
                {'t': 'Cover and seek care', 'd': 'Apply dressing and visit clinician for possible antibiotics.', 'x': ''},
                {'t': 'Tetanus/rabies', 'd': 'Assess need for tetanus or rabies prophylaxis.', 'x': ''},
                {'t': 'Do not close', 'd': 'Do not attempt to suture at home unless advised.', 'x': ''},
                {'t': 'Watch for signs', 'd': 'Rapid infection is common — seek care if red or painful.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Minor Fracture',
            'summary': 'Small bone breaks — immobilize and seek imaging if suspect.',
            'steps': [
                {'t': 'Immobilize', 'd': 'Use a splint or supportive padding to keep still.', 'x': ''},
                {'t': 'Ice', 'd': 'Apply ice to reduce swelling.', 'x': ''},
                {'t': 'Elevate', 'd': 'Keep limb raised if possible.', 'x': ''},
                {'t': 'Seek X-ray', 'd': 'Get medical evaluation and imaging.', 'x': ''},
                {'t': 'Pain management', 'd': 'Use analgesics as appropriate.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Swelling',
            'summary': 'Localized swelling often due to injury or allergy; reduce and monitor.',
            'steps': [
                {'t': 'Rest', 'd': 'Avoid using the area.', 'x': ''},
                {'t': 'Ice', 'd': 'Apply ice for 15–20 minutes periodically.', 'x': ''},
                {'t': 'Compress', 'd': 'Use compression bandage for limbs if appropriate.', 'x': ''},
                {'t': 'Elevate', 'd': 'Raise area above heart level to reduce swelling.', 'x': ''},
                {'t': 'See doctor', 'd': 'If swelling is severe, spreading, or with breathing difficulty seek urgent care.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Eye Irritation',
            'summary': 'Irritation or foreign body sensation in eye; flush and protect vision.',
            'steps': [
                {'t': 'Do not rub', 'd': 'Avoid rubbing the eye.', 'x': ''},
                {'t': 'Flush with water', 'd': 'Irrigate the eye with clean water for 10–15 minutes.', 'x': ''},
                {'t': 'Cover', 'd': 'Use a loose eye shield if painful.', 'x': ''},
                {'t': 'Seek care', 'd': 'If vision is affected or chemical exposure occurred, get urgent ophthalmic care.', 'x': ''},
                {'t': 'Avoid drops', 'd': 'Do not use topical drops unless prescribed.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Minor Wound',
            'summary': 'Small open wound—clean and dress to prevent infection.',
            'steps': [
                {'t': 'Rinse', 'd': 'Clean with running water to remove debris.', 'x': ''},
                {'t': 'Apply antiseptic', 'd': 'Use antiseptic solution or ointment.', 'x': ''},
                {'t': 'Cover', 'd': 'Use sterile dressing and change daily.', 'x': ''},
                {'t': 'Tetanus', 'd': 'Check tetanus status for dirty wounds.', 'x': ''},
                {'t': 'See clinician', 'd': 'If deep, have signs of infection, or do not heal.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Skin Infection',
            'summary': 'Infected skin may show spreading redness, warmth, and pus—seek medical review.',
            'steps': [
                {'t': 'Keep area clean', 'd': 'Gently wash and pat dry.', 'x': ''},
                {'t': 'Do not squeeze', 'd': 'Avoid trying to lance or drain at home.', 'x': ''},
                {'t': 'See clinician', 'd': 'Most skin infections need antibiotics.', 'x': ''},
                {'t': 'Cover if draining', 'd': 'Use clean dressing to absorb discharge.', 'x': ''},
                {'t': 'Watch for systemic', 'd': 'Seek emergency help for fever, spreading redness or rapid worsening.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Allergic Reaction',
            'summary': 'Mild to severe allergy signs—treat symptoms and seek urgent care for systemic signs.',
            'steps': [
                {'t': 'Stop exposure', 'd': 'Remove the trigger if possible.', 'x': ''},
                {'t': 'Antihistamine', 'd': 'Give oral antihistamine for mild reactions.', 'x': ''},
                {'t': 'Epinephrine', 'd': 'If breathing or airway is compromised, administer epinephrine and call emergency services.', 'x': ''},
                {'t': 'Monitor', 'd': 'Observe for progression of symptoms.', 'x': ''},
                {'t': 'See clinician', 'd': 'Follow up with healthcare for ongoing management.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Blister',
            'summary': 'Fluid-filled skin lesion from friction or heat—protect and avoid popping.',
            'steps': [
                {'t': 'Protect', 'd': 'Cover with a non-stick dressing to protect.', 'x': ''},
                {'t': 'Do not pop', 'd': 'Avoid puncturing unless large and painful; seek advice.', 'x': ''},
                {'t': 'If popped, clean', 'd': 'Rinse and apply antibiotic dressing.', 'x': ''},
                {'t': 'Reduce pressure', 'd': 'Use padding to offload friction.', 'x': ''},
                {'t': 'Watch for infection', 'd': 'Redness, warmth or pus needs review.', 'x': ''}
            ]
        }
    ]

    for g in guidance_data:
        FirstAidGuidance.objects.update_or_create(
            injury_type=g['injury_type'],
            defaults={'summary': g['summary'], 'steps': g['steps']}
        )


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_comprehensive_injury_guidance'),
    ]

    operations = [
        migrations.RunPython(create_additional_guidance)
    ]
