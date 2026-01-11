"""Middleware for request logging and monitoring"""
from django.utils.deprecation import MiddlewareMixin
import logging
import time
import json

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log all HTTP requests with timing information"""
    
    def process_request(self, request):
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            log_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'user': str(request.user_obj.id) if hasattr(request, 'user_obj') else 'anonymous',
            }
            
            # Log level based on status code
            if response.status_code >= 500:
                logger.error(f"Request completed with error", extra=log_data)
            elif response.status_code >= 400:
                logger.warning(f"Request failed", extra=log_data)
            else:
                logger.info(f"Request completed", extra=log_data)
        
        return response


class ErrorResponseMiddleware(MiddlewareMixin):
    """Standardize error responses"""
    
    def process_exception(self, request, exception):
        """Catch unhandled exceptions and return standardized response"""
        from rest_framework.response import Response
        from rest_framework import status
        
        logger.exception(f"Unhandled exception in {request.method} {request.path}", exc_info=exception)
        
        return Response({
            'error': True,
            'message': 'Internal server error',
            'code': 'SERVER_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
