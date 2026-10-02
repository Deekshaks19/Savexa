from django.db import migrations


def create_comprehensive_guidance(apps, schema_editor):
    FirstAidGuidance = apps.get_model('api', 'FirstAidGuidance')
    
    guidance_data = [
        # BURNS
        {
            'injury_type': '1st Degree Burn',
            'summary': 'Mild burn - skin is red but not blistered. Cool it down quickly.',
            'steps': [
                {'t': 'Cool the burn', 'd': 'Run cool water on it for 10-15 minutes.', 'x': 'Use cool water, not ice.'},
                {'t': 'Dry gently', 'd': 'Pat dry with a clean cloth.', 'x': ''},
                {'t': 'Apply aloe vera', 'd': 'Spread aloe gel to soothe the skin.', 'x': 'Or use moisturizer.'},
                {'t': 'Take pain relief', 'd': 'Use paracetamol or ibuprofen if it hurts.', 'x': ''},
                {'t': 'Protect from sun', 'd': 'Keep the area covered from sun for a few days.', 'x': ''}
            ]
        },
        {
            'injury_type': '2nd Degree Burn',
            'summary': 'Moderate burn - skin is red and blistered. Needs careful care.',
            'steps': [
                {'t': 'Cool it down', 'd': 'Run cool water for 15-20 minutes.', 'x': 'Do not use ice.'},
                {'t': 'Do not pop blisters', 'd': 'Leave blisters alone - they protect the skin.', 'x': 'Breaking them causes infection.'},
                {'t': 'Cover loosely', 'd': 'Use a clean, non-stick bandage or cloth.', 'x': ''},
                {'t': 'Pain relief', 'd': 'Take medicine for pain.', 'x': ''},
                {'t': 'Watch for infection', 'd': 'Look for pus, increasing redness, or fever.', 'x': 'See a doctor if infected.'}
            ]
        },
        {
            'injury_type': '3rd Degree Burn',
            'summary': 'Severe burn - skin is blackened or white. CALL EMERGENCY immediately.',
            'steps': [
                {'t': 'CALL 911', 'd': 'Get emergency help right now.', 'x': 'This is life-threatening.'},
                {'t': 'Do not remove clothing', 'd': 'Leave burned clothes on if stuck.', 'x': 'Removing them causes more damage.'},
                {'t': 'Cover if possible', 'd': 'Drape a clean cloth loosely over the area.', 'x': ''},
                {'t': 'Keep person calm', 'd': 'Talk to them, keep them warm.', 'x': ''},
                {'t': 'Wait for help', 'd': 'Do not move the person unless in danger.', 'x': ''}
            ]
        },
        
        # CUTS
        {
            'injury_type': 'Minor Cut',
            'summary': 'Small cut that is bleeding lightly. Easy to treat at home.',
            'steps': [
                {'t': 'Apply pressure', 'd': 'Press with a clean cloth for 5 minutes.', 'x': 'This stops bleeding.'},
                {'t': 'Wash with water', 'd': 'Rinse gently under running water.', 'x': 'Remove dirt and germs.'},
                {'t': 'Apply ointment', 'd': 'Use antibiotic cream if you have it.', 'x': ''},
                {'t': 'Bandage', 'd': 'Cover with a clean bandage.', 'x': ''},
                {'t': 'Change bandage daily', 'd': 'Keep it clean and dry.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Deep Cut',
            'summary': 'Large or deep cut that won\'t stop bleeding. Needs medical care.',
            'steps': [
                {'t': 'Apply firm pressure', 'd': 'Press hard with a clean cloth for 10+ minutes.', 'x': 'Do not peek.'},
                {'t': 'Elevate', 'd': 'Raise the cut area above heart level.', 'x': 'This slows bleeding.'},
                {'t': 'Call 911', 'd': 'If bleeding does not stop, get emergency help.', 'x': ''},
                {'t': 'Prepare for hospital', 'd': 'Keep applying pressure while waiting.', 'x': 'May need stitches.'},
                {'t': 'Do not wash yet', 'd': 'Doctor will clean it properly.', 'x': ''}
            ]
        },
        
        # SPRAINS
        {
            'injury_type': 'Ankle Sprain',
            'summary': 'Twisted ankle with pain and swelling. Use RICE method.',
            'steps': [
                {'t': 'Rest', 'd': 'Stop walking, sit or lie down.', 'x': 'Do not put weight on it.'},
                {'t': 'Ice', 'd': 'Put ice wrapped in cloth for 20 minutes, 3-4 times daily.', 'x': 'First 48 hours.'},
                {'t': 'Compress', 'd': 'Wrap with elastic bandage - snug but not tight.', 'x': ''},
                {'t': 'Elevate', 'd': 'Keep ankle above hip level.', 'x': 'Use pillow to prop it up.'},
                {'t': 'Check after 2 days', 'd': 'If still bad, see a doctor for X-ray.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Wrist Sprain',
            'summary': 'Twisted wrist with pain. Needs support and rest.',
            'steps': [
                {'t': 'Stop using it', 'd': 'Rest your wrist completely.', 'x': 'Do not use for writing or gripping.'},
                {'t': 'Ice', 'd': 'Apply ice for 15-20 minutes, 4 times daily.', 'x': ''},
                {'t': 'Wrap it', 'd': 'Use elastic bandage or wrist brace.', 'x': ''},
                {'t': 'Elevation', 'd': 'Keep hand raised on a pillow.', 'x': ''},
                {'t': 'Pain relief', 'd': 'Take paracetamol or ibuprofen.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Knee Sprain',
            'summary': 'Twisted or injured knee. Follow RICE method.',
            'steps': [
                {'t': 'Stop activity', 'd': 'Do not bend or put weight on knee.', 'x': ''},
                {'t': 'Ice immediately', 'd': 'Apply ice for 20 minutes, repeat every 2-3 hours.', 'x': ''},
                {'t': 'Compress', 'd': 'Wrap with elastic bandage firmly.', 'x': ''},
                {'t': 'Elevate', 'd': 'Put knee on pillow while sitting or lying.', 'x': ''},
                {'t': 'See doctor', 'd': 'Get checked if swelling or pain doesn\'t improve.', 'x': ''}
            ]
        },
        
        # FRACTURES
        {
            'injury_type': 'Arm Fracture',
            'summary': 'Broken arm bone. Immobilize immediately and get to hospital.',
            'steps': [
                {'t': 'Immobilize', 'd': 'Keep arm still - do not move it.', 'x': 'Use sling if available.'},
                {'t': 'Ice', 'd': 'Apply ice wrapped in cloth to reduce swelling.', 'x': ''},
                {'t': 'Elevation', 'd': 'Keep arm raised on pillow.', 'x': ''},
                {'t': 'Call emergency', 'd': 'Call 911 for transport to hospital.', 'x': ''},
                {'t': 'X-ray', 'd': 'Hospital will take X-rays and apply cast.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Leg Fracture',
            'summary': 'Broken leg bone. Do not move. Call 911 immediately.',
            'steps': [
                {'t': 'Do not move', 'd': 'Keep leg completely still.', 'x': 'Movement causes more damage.'},
                {'t': 'Lie flat', 'd': 'Lie down and keep leg straight.', 'x': ''},
                {'t': 'Ice', 'd': 'Apply ice if available.', 'x': ''},
                {'t': 'Call 911', 'd': 'Get emergency medical help.', 'x': 'Do not try to walk.'},
                {'t': 'Wait for help', 'd': 'Keep talking to keep person calm.', 'x': ''}
            ]
        },
        
        # ABRASION
        {
            'injury_type': 'Abrasion/Scrape',
            'summary': 'Scraped skin from fall. Easy to treat but needs cleaning.',
            'steps': [
                {'t': 'Rinse gently', 'd': 'Use clean water to wash away dirt.', 'x': 'Be gentle to avoid pain.'},
                {'t': 'Pat dry', 'd': 'Use clean cloth to dry.', 'x': 'Do not rub.'},
                {'t': 'Antibiotic cream', 'd': 'Apply antibiotic ointment.', 'x': 'Helps prevent infection.'},
                {'t': 'Bandage', 'd': 'Cover with non-stick bandage.', 'x': ''},
                {'t': 'Keep clean', 'd': 'Change bandage daily.', 'x': 'Watch for infection signs.'}
            ]
        },
        
        # BLEEDING
        {
            'injury_type': 'Severe Bleeding',
            'summary': 'Heavy bleeding that won\'t stop. This is an emergency.',
            'steps': [
                {'t': 'CALL 911', 'd': 'Get emergency help immediately.', 'x': ''},
                {'t': 'Apply pressure', 'd': 'Press hard with clean cloth on wound.', 'x': 'Use both hands if needed.'},
                {'t': 'Do not remove cloth', 'd': 'Add more cloth on top if it soaks through.', 'x': 'Removing it stops clotting.'},
                {'t': 'Elevate', 'd': 'Raise wound above heart if safe.', 'x': ''},
                {'t': 'Keep pressure', 'd': 'Maintain pressure until help arrives.', 'x': ''}
            ]
        },
        {
            'injury_type': 'Nosebleed',
            'summary': 'Bleeding from nose. Usually stops on its own.',
            'steps': [
                {'t': 'Sit up', 'd': 'Sit upright and lean forward slightly.', 'x': 'This prevents swallowing blood.'},
                {'t': 'Pinch nose', 'd': 'Squeeze both nostrils closed for 10 minutes.', 'x': 'Do not let go early.'},
                {'t': 'Use ice', 'd': 'Hold ice pack on nose.', 'x': 'Constricts blood vessels.'},
                {'t': 'Breathe through mouth', 'd': 'Do not breathe through nose.', 'x': ''},
                {'t': 'If it continues', 'd': 'See doctor if bleeding lasts over 30 minutes.', 'x': ''}
            ]
        },
        
        # BRUISE
        {
            'injury_type': 'Bruise',
            'summary': 'Black and blue mark from impact. Usually heals on its own.',
            'steps': [
                {'t': 'Ice', 'd': 'Apply ice for 15 minutes in first few hours.', 'x': 'Reduces swelling.'},
                {'t': 'Rest', 'd': 'Avoid using the bruised area.', 'x': ''},
                {'t': 'Compress', 'd': 'Wrap gently with elastic bandage.', 'x': ''},
                {'t': 'Elevate', 'd': 'Keep area raised if possible.', 'x': ''},
                {'t': 'Pain relief', 'd': 'Take pain medication if needed.', 'x': 'Usually fades in 1-2 weeks.'}
            ]
        },
        
        # INSECT BITES
        {
            'injury_type': 'Insect Bite',
            'summary': 'Sting or bite from insect. Causes itching and mild swelling.',
            'steps': [
                {'t': 'Remove stinger', 'd': 'If visible, scrape it out with flat edge.', 'x': 'Do not squeeze.'},
                {'t': 'Wash area', 'd': 'Rinse with soap and water.', 'x': ''},
                {'t': 'Apply ice', 'd': 'Ice reduces pain and swelling.', 'x': 'Use for 10-15 minutes.'},
                {'t': 'Antihistamine', 'd': 'Take allergy medicine or cream to stop itch.', 'x': ''},
                {'t': 'Do not scratch', 'd': 'Keep area clean to avoid infection.', 'x': 'Scratching spreads germs.'}
            ]
        },
        
        # SNAKE BITE
        {
            'injury_type': 'Snake Bite',
            'summary': 'Bitten by snake. May be venomous. CALL 911 immediately.',
            'steps': [
                {'t': 'CALL 911', 'd': 'Get emergency help right away.', 'x': 'Some snakes are deadly.'},
                {'t': 'Stay calm', 'd': 'Reduce activity - venom spreads with movement.', 'x': ''},
                {'t': 'Remove jewelry', 'd': 'Take off rings, bracelets from bitten area.', 'x': 'Swelling may cut off circulation.'},
                {'t': 'Wash gently', 'd': 'Rinse with soap and water if no antivenom.', 'x': ''},
                {'t': 'Keep still', 'd': 'Do not move bitten area until help arrives.', 'x': ''}
            ]
        },
        
        # HEAD INJURY
        {
            'injury_type': 'Head Injury',
            'summary': 'Hit to head. May cause concussion. Monitor closely.',
            'steps': [
                {'t': 'Stop activity', 'd': 'Stop all sports and rest immediately.', 'x': ''},
                {'t': 'Watch for signs', 'd': 'Look for dizziness, confusion, nausea, headache.', 'x': ''},
                {'t': 'See doctor', 'd': 'Get checked even if feeling okay.', 'x': 'Symptoms may appear later.'},
                {'t': 'Rest', 'd': 'Avoid physical activity for several days.', 'x': ''},
                {'t': 'No return yet', 'd': 'Do not go back to sport until cleared by doctor.', 'x': ''}
            ]
        },
        
        # EYE INJURY
        {
            'injury_type': 'Eye Injury',
            'summary': 'Damage to eye area. Could affect vision. See doctor urgently.',
            'steps': [
                {'t': 'Do not rub', 'd': 'Keep hands away from eye.', 'x': 'May cause more damage.'},
                {'t': 'Flush if needed', 'd': 'If chemical splash, rinse with water for 15 minutes.', 'x': ''},
                {'t': 'Cover gently', 'd': 'Place clean cloth loosely over eye.', 'x': ''},
                {'t': 'Ice', 'd': 'Apply ice pack gently to reduce swelling.', 'x': ''},
                {'t': 'See eye doctor', 'd': 'Get professional help immediately.', 'x': 'Vision issues need urgent care.'}
            ]
        },
        
        # CHEMICAL BURN
        {
            'injury_type': 'Chemical Burn',
            'summary': 'Skin burned by chemical. Flush immediately with water.',
            'steps': [
                {'t': 'Flush with water', 'd': 'Rinse with water for at least 15-20 minutes.', 'x': 'This is most important.'},
                {'t': 'Remove clothing', 'd': 'Take off contaminated clothes if safe.', 'x': 'Be careful not to touch chemical.'},
                {'t': 'Keep flushing', 'd': 'Continue rinsing while going to hospital.', 'x': ''},
                {'t': 'Call 911', 'd': 'Get emergency medical help.', 'x': 'Chemical burns are serious.'},
                {'t': 'Take container', 'd': 'Bring the chemical container to hospital.', 'x': 'Helps doctors treat properly.'}
            ]
        },
        
        # ELECTRICAL BURN
        {
            'injury_type': 'Electrical Burn',
            'summary': 'Burned by electricity. Can be life-threatening. Call 911.',
            'steps': [
                {'t': 'CALL 911', 'd': 'Get emergency help immediately.', 'x': 'Even if seems minor.'},
                {'t': 'Do not touch person', 'd': 'If still in contact with electricity, do not touch.', 'x': 'You can be electrocuted too.'},
                {'t': 'Turn off power', 'd': 'If safe, turn off the electrical source.', 'x': 'Use non-metal object if needed.'},
                {'t': 'CPR if needed', 'd': 'If unconscious, do CPR if trained.', 'x': 'Electricity can stop heart.'},
                {'t': 'Cover burns', 'd': 'Use clean cloth to cover burn areas.', 'x': ''}
            ]
        },
        
        # CHOKING
        {
            'injury_type': 'Choking',
            'summary': 'Object stuck in throat. Blocking airway. Act immediately.',
            'steps': [
                {'t': 'Encourage coughing', 'd': 'Ask person to cough hard.', 'x': 'Coughing often dislodges object.'},
                {'t': 'Heimlich maneuver', 'd': 'Stand behind, push upward on abdomen.', 'x': 'Quick hard thrusts.'},
                {'t': 'Repeat', 'd': 'Do 5 abdominal thrusts, then check if cleared.', 'x': 'Repeat if needed.'},
                {'t': 'Call 911', 'd': 'If object not cleared, call emergency.', 'x': ''},
                {'t': 'Recovery position', 'd': 'Once cleared, monitor breathing.', 'x': 'May have throat injury.'}
            ]
        },
    ]

    for item in guidance_data:
        FirstAidGuidance.objects.update_or_create(
            injury_type=item['injury_type'],
            defaults={
                'summary': item['summary'],
                'steps': item['steps'],
            }
        )


def delete_all_guidance(apps, schema_editor):
    FirstAidGuidance = apps.get_model('api', 'FirstAidGuidance')
    FirstAidGuidance.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_add_more_guidance'),
    ]

    operations = [
        migrations.RunPython(create_comprehensive_guidance, delete_all_guidance),
    ]
