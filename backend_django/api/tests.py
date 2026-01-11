# Tests for Django API

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from .models import User, Complaint
import json
import bcrypt


class AuthenticationTestCase(TestCase):
    """Test user authentication endpoints"""
    
    def setUp(self):
        self.client = Client()
        
    def test_password_strength_validation(self):
        """Test password strength requirements in serializer"""
        from .serializers import RegisterSerializer
        
        # No uppercase
        data = {
            'name': 'Test', 'email': 'test@example.com',
            'password': 'lowercase123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
        # No number
        data['password'] = 'NoNumber'
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
        # Valid
        data['password'] = 'ValidPass123'
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class ComplaintValidationTestCase(TestCase):
    """Test complaint input validation"""
    
    def test_complaint_title_validation(self):
        """Test that complaint titles meet minimum length"""
        from .serializers import ComplaintSubmitSerializer
        
        # Too short
        data = {'title': 'a', 'description': 'This is a valid description', 'location': 'Main St'}
        serializer = ComplaintSubmitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
        # Valid
        data = {'title': 'Valid Title Issue', 'description': 'This is a valid description for testing', 'location': 'Main St'}
        serializer = ComplaintSubmitSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_complaint_description_validation(self):
        """Test description length requirements"""
        from .serializers import ComplaintSubmitSerializer
        
        # Too short
        data = {'title': 'Valid Title', 'description': 'short', 'location': 'Main St'}
        serializer = ComplaintSubmitSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class ErrorHandlingTestCase(TestCase):
    """Test standardized error responses"""
    
    def test_validation_error_response(self):
        """Test that validation errors use standardized format"""
        from .errors import StandardError
        from rest_framework import status
        
        response = StandardError.validation_error({'email': ['Invalid email format']})
        data = response.data
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(data['error'])
        self.assertEqual(data['code'], 'VALIDATION_ERROR')
        self.assertIn('details', data)
    
    def test_auth_error_response(self):
        """Test auth error response format"""
        from .errors import StandardError
        from rest_framework import status
        
        response = StandardError.auth_error('Invalid token')
        data = response.data
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(data['error'])
        self.assertEqual(data['code'], 'AUTH_ERROR')
    
    def test_success_response(self):
        """Test success response format"""
        from .errors import StandardError
        from rest_framework import status
        
        response = StandardError.success_response(
            data={'id': '123', 'name': 'Test'},
            message='Operation successful'
        )
        data = response.data
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(data['error'])
        self.assertEqual(data['message'], 'Operation successful')
        self.assertIn('data', data)


class NLPClassifierTestCase(TestCase):
    """Test multi-department routing functionality"""
    
    def test_multi_department_detection(self):
        """Test that NLP classifier detects multiple relevant departments"""
        from .nlp_classifier import classifier
        
        # Complaint involving multiple departments
        result = classifier.classify_multi_department(
            'The road has deep potholes causing accidents and water is leaking from pipes'
        )
        
        # Should detect multiple departments
        self.assertIn('multiDepartmentRouting', result)
        self.assertIn('departments', result)
        self.assertGreater(len(result['departments']), 0)
        self.assertIn('departmentDetails', result)
    
    def test_confidence_scores(self):
        """Test confidence scoring in multi-department routing"""
        from .nlp_classifier import classifier
        
        result = classifier.classify_multi_department('Power outage in the area')
        
        # Check structure
        self.assertIn('confidenceScore', result)
        self.assertIn('departmentDetails', result)
        
        # All confidence scores should be between 0 and 1
        for dept_detail in result['departmentDetails']:
            self.assertGreaterEqual(dept_detail['confidence'], 0)
            self.assertLessEqual(dept_detail['confidence'], 1)
