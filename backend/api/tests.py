from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework.test import APIClient


class ApiContractTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def image_upload(self):
		buffer = BytesIO()
		Image.new('RGB', (32, 32), color=(180, 80, 40)).save(buffer, format='PNG')
		return SimpleUploadedFile('test.png', buffer.getvalue(), content_type='image/png')

	def test_detect_requires_image(self):
		response = self.client.post('/api/detect/')
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.data['error'], 'No image file provided')

	def test_detect_rejects_invalid_file(self):
		upload = SimpleUploadedFile('not-an-image.txt', b'not an image', content_type='text/plain')
		response = self.client.post('/api/detect/', {'image': upload})
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.data['error'], 'Invalid image file')

	@patch('api.views.InjuryDetection.objects.create', return_value=SimpleNamespace(id=1))
	@patch('api.views.model')
	def test_detect_returns_class_and_guidance(self, mock_model, _mock_create):
		mock_model.predict.return_value = np.array([[0.01, 0.01, 0.90, 0.02, 0.02, 0.02, 0.02]])
		with patch('api.views.MODEL_LOADED', True):
			response = self.client.post('/api/detect/', {'image': self.image_upload()})
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['injury_type'], 'Abrasions')
		self.assertEqual(response.data['guidance']['injury_type'], 'Abrasion')
		self.assertEqual(response.data['region'], 'Not specified')

	def test_chat_requires_message(self):
		response = self.client.post('/api/chat/', {}, format='json')
		self.assertEqual(response.status_code, 400)

	def test_chat_returns_database_guidance(self):
		response = self.client.post('/api/chat/', {'message': 'What should I do for a burn?'}, format='json')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['source'], 'guidance_database')
		self.assertIn('Burn', response.data['answer'])
