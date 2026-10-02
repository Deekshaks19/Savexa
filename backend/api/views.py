from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
import os
import sys
from PIL import Image
import numpy as np
# Create logger early so it can be used during TensorFlow import
logger = logging.getLogger(__name__)

import tensorflow as tf

from .models import InjuryDetection, FirstAidGuidance
from .serializers import InjuryDetectionSerializer, FirstAidGuidanceSerializer

# Model path (project root -> cv/aidsense/models/aidSense_model.h5)
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'cv', 'aidsense', 'models', 'aidSense_multiclass.h5')
)

CENTROIDS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'cv', 'aidsense', 'models', 'class_centroids.json')
)

MODEL_LOADED = False
model = None
embedding_model = None
print('Resolved MODEL_PATH:', MODEL_PATH)
print('Model file exists:', os.path.exists(MODEL_PATH))
print('Current PID:', os.getpid())
print('Python executable:', sys.executable)
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    if model.output_shape[-1] != 7:
        raise ValueError(f'Expected seven model outputs, found {model.output_shape[-1]}')
    MODEL_LOADED = True
    print('MODEL LOADED SUCCESSFULLY:', MODEL_PATH)
    embedding_model = tf.keras.Model(inputs=model.input, outputs=model.get_layer("global_average_pooling").output)
    print('EMBEDDING MODEL EXTRACTED SUCCESSFULLY')
except Exception:
    import traceback
    print('MODEL LOAD FAILED')
    traceback.print_exc()
    MODEL_LOADED = False
    embedding_model = None


INJURY_CLASSES = [
    'Burn',
    'Cut',
    'Abrasions',
    'Bruises',
    'Laceration',
    'Stab_wound',
    'Animal_bite',
]

FALLBACK_GUIDANCE_MAP = {
    'burn': ['Burn'],
    'cut': ['Cut'],
    'abrasion': ['Abrasion'],
    'abrasions': ['Abrasion'],
    'scrape': ['Abrasion'],
    'scratch': ['Abrasion'],
    'bruise': ['Bruise'],
    'bruises': ['Bruise'],
    'laceration': ['Minor Wound', 'Cut'],
    'stab_wound': ['Minor Wound'],
    'animal_bite': ['Animal Bite'],
    'animal bite': ['Animal Bite'],
    'rash': ['Rash'],
    'insect bite': ['Insect Bite'],
    'bee sting': ['Bee Sting'],
    'dog bite': ['Dog Bite'],
    'cat bite': ['Cat Bite'],
    'fracture': ['Fracture'],
    'sprain': ['Sprain'],
}


def preprocess_image(image_file):
    """Open image, convert to RGB, resize to (224,224), normalize to 0-1 and expand dims.

    Args:
        image_file: Uploaded file-like object (InMemoryUploadedFile or similar)

    Returns:
        np.ndarray: Array shaped (1, 224, 224, 3) dtype float32
    """
    try:
        img = Image.open(image_file)
        img = img.convert('RGB')
        img = img.resize((224, 224), Image.BILINEAR)
        arr = np.asarray(img, dtype=np.float32) / 255.0
        return np.expand_dims(arr, axis=0)
    except Exception as exc:
        logger.exception('Error preprocessing image: %s', exc)
        raise ValueError('Invalid image file')


def get_injury_guidance(injury_type):
    """Retrieve `FirstAidGuidance` for an injury type with fallbacks.

    Returns None if nothing matches.
    """
    if not injury_type:
        return None

    try:
        guidance = FirstAidGuidance.objects.filter(injury_type__iexact=injury_type).first()
        if guidance:
            return guidance

        # Keyword fallback matching
        normalized = injury_type.strip().lower()
        for keyword, candidates in FALLBACK_GUIDANCE_MAP.items():
            if keyword in normalized:
                for candidate in candidates:
                    guidance = FirstAidGuidance.objects.filter(injury_type__iexact=candidate).first()
                    if guidance:
                        return guidance

        # Last resort: contains match
        guidance = FirstAidGuidance.objects.filter(injury_type__icontains=injury_type).first()
        return guidance
    except Exception as exc:
        logger.exception('Database error when retrieving guidance for %s: %s', injury_type, exc)
        return None


@api_view(['GET'])
def test_api(request):
    return Response({
        'message': 'Backend API is working!',
        'model_loaded': bool(MODEL_LOADED),
        'model_exists': os.path.exists(MODEL_PATH),
        'model_path': MODEL_PATH,
    })


@api_view(['POST'])
def detect_injury(request):
    """Accept an image and run AI detection, store and return results."""
    if not MODEL_LOADED or model is None:
        logger.error('Detection requested but model is not loaded')
        return Response({'error': 'TensorFlow model not loaded'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if 'image' not in request.FILES:
        logger.warning('No image file in request')
        return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)

    image_file = request.FILES.get('image')

    try:
        img_array = preprocess_image(image_file)
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        preds = model.predict(img_array, verbose=0)
    except Exception as exc:
        logger.exception('TensorFlow prediction error: %s', exc)
        return Response({'error': 'Model prediction failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        scores = np.array(preds[0], dtype=float)
        predicted_idx = int(np.argmax(scores))
        ai_confidence = float(scores[predicted_idx]) * 100.0
    except Exception as exc:
        logger.exception('Error parsing prediction output: %s', exc)
        return Response({'error': 'Invalid prediction output'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if 0 <= predicted_idx < len(INJURY_CLASSES):
        injury_type = INJURY_CLASSES[predicted_idx]
    else:
        injury_type = 'Unknown Injury'

    confidence = ai_confidence
    if confidence >= 90:
        severity = 'critical'
    elif confidence >= 75:
        severity = 'high'
    elif confidence >= 60:
        severity = 'moderate'
    else:
        severity = 'low'

    # Compute cosine similarity and validity based on embeddings and centroids
    valid = True
    similarity = None
    if embedding_model is not None:
        try:
            emb = embedding_model.predict(img_array, verbose=0)[0]
            if os.path.exists(CENTROIDS_PATH):
                import json
                with open(CENTROIDS_PATH, 'r') as f:
                    centroids = json.load(f)
                if injury_type in centroids:
                    centroid = np.array(centroids[injury_type])
                    norm_emb = np.linalg.norm(emb)
                    norm_centroid = np.linalg.norm(centroid)
                    similarity = float(np.dot(emb, centroid) / (norm_emb * norm_centroid + 1e-8))
                    # Cosine similarity threshold of 0.60 for OOD invalid-image rejection
                    if similarity < 0.60:
                        valid = False
        except Exception as exc:
            logger.exception('Error calculating embedding similarity: %s', exc)

    RECOMMENDATION_MAP = {
        'critical': 'Seek immediate medical attention.',
        'high': 'Apply first aid and contact a medical professional promptly.',
        'moderate': 'Provide first aid and monitor symptoms closely.',
        'low': 'Use basic first aid and observe for changes.',
    }
    recommendation = RECOMMENDATION_MAP.get(severity, 'Provide first aid and monitor closely.')

    region = 'Not specified'

    # Retrieve guidance from DB
    guidance = get_injury_guidance(injury_type)
    guidance_data = FirstAidGuidanceSerializer(guidance).data if guidance else None

    # Save detection record
    try:
        detection = InjuryDetection.objects.create(
            injury_type=injury_type,
            region=region,
            severity=severity,
            confidence=round(float(confidence), 2),
            image=image_file,
        )
    except Exception as exc:
        logger.exception('Failed to save InjuryDetection: %s', exc)
        return Response({'error': 'Failed to save detection'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Build all predictions payload
    try:
        all_injuries = list(FirstAidGuidance.objects.values_list('injury_type', flat=True))
    except Exception:
        all_injuries = []

    all_predictions = {
        'AI_Prediction': {'injury': injury_type, 'confidence': round(ai_confidence, 2)},
        'Available_Injuries': sorted(all_injuries),
    }

    response_data = {
        'detection_id': detection.id,
        'injury_type': injury_type,
        'region': region,
        'severity': severity,
        'confidence': round(float(confidence), 2),
        'guidance': guidance_data,
        'emergency_recommendation': recommendation,
        'ai_prediction': injury_type,
        'ai_confidence': round(ai_confidence, 2),
        'manual_selection': False,
        'all_predictions': all_predictions,
        'valid': valid,
        'similarity': round(similarity, 4) if similarity is not None else None,
    }

    logger.info('Detection saved id=%s injury=%s confidence=%.2f valid=%s similarity=%s',
                detection.id, injury_type, ai_confidence, valid, similarity)
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_all_detections(request):
    """Return all stored InjuryDetection objects."""
    try:
        detections = InjuryDetection.objects.all()
        serializer = InjuryDetectionSerializer(detections, many=True)
        return Response(serializer.data)
    except Exception as exc:
        logger.exception('Error fetching detections: %s', exc)
        return Response({'error': 'Failed to fetch detections'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_guidance(request, injury_type):
    """Return FirstAidGuidance for a given injury type or 404."""
    guidance = get_injury_guidance(injury_type)
    if not guidance:
        return Response({'error': f'No guidance found for {injury_type}'}, status=status.HTTP_404_NOT_FOUND)
    serializer = FirstAidGuidanceSerializer(guidance)
    return Response(serializer.data)


@api_view(['GET'])
def get_all_injury_types(request):
    """Return all FirstAidGuidance entries."""
    try:
        all_injuries = FirstAidGuidance.objects.all()
        serializer = FirstAidGuidanceSerializer(all_injuries, many=True)
        return Response({'injury_types': serializer.data, 'total': all_injuries.count()})
    except Exception as exc:
        logger.exception('Error fetching injury types: %s', exc)
        return Response({'error': 'Failed to fetch injury types'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def chat_assistant(request):
    """Answer first-aid questions from the approved guidance database."""
    message = str(request.data.get('message', '')).strip()
    if not message:
        return Response({'error': 'A message is required'}, status=status.HTTP_400_BAD_REQUEST)

    guidance = None
    for keyword in (
        'burn', 'scald', 'cut', 'laceration', 'wound', 'bleed', 'abrasion',
        'scrape', 'bruise', 'bite', 'sting', 'fracture', 'broken', 'sprain',
        'chok', 'cpr', 'rash', 'allerg', 'head injury', 'nosebleed', 'shock',
    ):
        if keyword in message.lower():
            guidance = get_injury_guidance(keyword)
            if guidance:
                break

    if not guidance:
        return Response({
            'answer': 'I can provide first-aid guidance for burns, cuts, abrasions, bruises, bites, sprains, choking, CPR, and related topics. I cannot diagnose an injury. For a serious or life-threatening situation, contact emergency services.',
            'source': 'guidance_database',
        })

    steps = []
    for step in guidance.steps or []:
        title = step.get('t', 'Step')
        description = step.get('d', '')
        note = step.get('x', '')
        text = f'{title}: {description}'
        if note:
            text += f' Note: {note}'
        steps.append(text)

    answer = f'{guidance.injury_type}: {guidance.summary}\n\n' + '\n'.join(
        f'{index}. {step}' for index, step in enumerate(steps, 1)
    )
    answer += '\n\nThis is general first-aid information, not a diagnosis. Seek professional care when symptoms are severe, worsening, or unclear.'
    return Response({'answer': answer, 'source': 'guidance_database', 'injury_type': guidance.injury_type})
