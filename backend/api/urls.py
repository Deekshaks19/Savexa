from django.urls import path
from .views import (
    test_api,
    detect_injury,
    get_all_detections,
    get_guidance,
    get_all_injury_types,
    chat_assistant,
)

urlpatterns = [
    path('test/', test_api, name='test_api'),
    path('detect/', detect_injury, name='detect_injury'),
    path('detections/', get_all_detections, name='get_detections'),
    path('guidance/<str:injury_type>/', get_guidance, name='get_guidance'),
    path('injury-types/', get_all_injury_types, name='get_all_injury_types'),
    path('chat/', chat_assistant, name='chat_assistant'),
]