import jwt
import datetime
from django.conf import settings
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .models import User


def get_auth_user(request):
    """Extract and validate JWT token from request header"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, 'Missing or invalid authorization header'
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user = User.objects.filter(id=payload['sub']).first()
        
        if not user:
            return None, 'User not found'
        
        return user, None
    except jwt.ExpiredSignatureError:
        return None, 'Token has expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'
    except Exception as e:
        return None, str(e)


def generate_token(user):
    """Generate JWT token for authenticated user"""
    payload = {
        'sub': str(user.id),
        'email': user.email,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=settings.JWT_EXPIRATION_DAYS)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def require_auth(f):
    """Decorator to require authentication for views"""
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        user, error = get_auth_user(request)
        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
        request.user_obj = user
        return f(request, *args, **kwargs)
    return decorated_function
