"""Standardized error response handling"""
from rest_framework.response import Response
from rest_framework import status
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class StandardError:
    """Standardized error response format"""
    
    @staticmethod
    def error_response(
        message: str,
        error_code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
        log_level: str = 'info'
    ) -> Response:
        """
        Return standardized error response
        
        Args:
            message: User-friendly error message
            error_code: Machine-readable error code (e.g., 'INVALID_INPUT')
            status_code: HTTP status code
            details: Additional error details
            log_level: Logging level ('info', 'warning', 'error', 'critical')
        """
        response_data = {
            'error': True,
            'message': message,
            'code': error_code,
        }
        
        if details:
            response_data['details'] = details
        
        # Log the error
        getattr(logger, log_level)(f"[{error_code}] {message}", extra={'details': details})
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def success_response(
        data: Any = None,
        message: str = 'Success',
        status_code: int = status.HTTP_200_OK
    ) -> Response:
        """Return standardized success response"""
        response_data = {
            'error': False,
            'message': message,
        }
        
        if data is not None:
            response_data['data'] = data
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def validation_error(errors: Dict[str, Any]) -> Response:
        """Return standardized validation error"""
        return StandardError.error_response(
            message='Validation error',
            error_code='VALIDATION_ERROR',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=errors
        )
    
    @staticmethod
    def auth_error(message: str = 'Authentication failed') -> Response:
        """Return standardized auth error"""
        return StandardError.error_response(
            message=message,
            error_code='AUTH_ERROR',
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def permission_error(message: str = 'Permission denied') -> Response:
        """Return standardized permission error"""
        return StandardError.error_response(
            message=message,
            error_code='PERMISSION_DENIED',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def not_found_error(message: str = 'Resource not found') -> Response:
        """Return standardized not found error"""
        return StandardError.error_response(
            message=message,
            error_code='NOT_FOUND',
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def server_error(message: str = 'Internal server error', details: Optional[Dict] = None) -> Response:
        """Return standardized server error"""
        return StandardError.error_response(
            message=message,
            error_code='SERVER_ERROR',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            log_level='error'
        )


# Error codes
ERROR_CODES = {
    'USER_EXISTS': 'User already exists',
    'USER_NOT_FOUND': 'User not found',
    'INVALID_CREDENTIALS': 'Invalid email or password',
    'TOKEN_EXPIRED': 'Authentication token has expired',
    'INVALID_TOKEN': 'Invalid authentication token',
    'UNAUTHORIZED': 'Unauthorized access',
    'COMPLAINT_NOT_FOUND': 'Complaint not found',
    'INVALID_STATUS': 'Invalid complaint status',
    'INVALID_INPUT': 'Invalid input provided',
    'MULTI_DEPT_ROUTING': 'Complaint routed to multiple departments',
}
