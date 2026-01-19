from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import bcrypt
import datetime

from .models import User, Department, Complaint, ComplaintHistory, Notification
from .errors import StandardError, ERROR_CODES
from .serializers import (
    UserSerializer, ComplaintSerializer, ComplaintHistorySerializer,
    NotificationSerializer, DepartmentSerializer, RegisterSerializer,
    LoginSerializer, ComplaintSubmitSerializer, StatusUpdateSerializer,
    ClassifyTextSerializer
)
from .auth import get_auth_user, generate_token, require_auth
from .utils import generate_complaint_id
from .nlp_classifier import classifier


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'ok',
        'message': 'Smart Griev Backend Running (Django + SQLite)'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return StandardError.validation_error(serializer.errors)
    
    data = serializer.validated_data
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'CITIZEN')
    department = data.get('department', '')
    phone = data.get('phone', '')
    
    # Block registration for ADMIN and OFFICER roles
    if role in ['ADMIN', 'OFFICER']:
        return StandardError.permission_error(
            message='Registration not allowed for admin or officer roles. Please contact system administrator.'
        )
    
    # Force role to CITIZEN for public registration
    role = 'CITIZEN'
    
    # Check if user exists
    if User.objects.filter(email=email).exists():
        return StandardError.error_response(
            message=ERROR_CODES['USER_EXISTS'],
            error_code='USER_EXISTS',
            status_code=status.HTTP_409_CONFLICT
        )
    
    try:
        # Hash password with increased cost factor (security improvement)
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        
        # Create user
        user = User.objects.create(
            email=email,
            password_hash=hashed,
            name=name,
            role=role,
            phone=phone,
            department=department if role == 'OFFICER' else None
        )
        
        # Generate token
        token = generate_token(user)
        
        return StandardError.success_response(
            data={
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'name': user.name,
                    'role': user.role,
                    'department': user.department
                },
                'session': {
                    'access_token': token
                }
            },
            message='User registered successfully',
            status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return StandardError.server_error(
            message='Registration failed',
            details={'error': str(e)}
        )


@api_view(['POST'])
def login(request):
    """Login user"""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return StandardError.validation_error(serializer.errors)
    
    email = serializer.validated_data.get('email')
    password = serializer.validated_data.get('password')
    
    try:
        user = User.objects.filter(email=email).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            token = generate_token(user)
            
            return StandardError.success_response(
                data={
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'name': user.name,
                        'phone': user.phone,
                        'role': user.role,
                        'department': user.department
                    },
                    'session': {
                        'access_token': token
                    }
                },
                message='Login successful'
            )
        else:
            return StandardError.auth_error(
                message=ERROR_CODES['INVALID_CREDENTIALS']
            )
    
    except Exception as e:
        return StandardError.server_error(
            message='Login failed',
            details={'error': str(e)}
        )


@api_view(['POST'])
@require_auth
def submit_complaint(request):
    """Submit a new complaint with multi-department routing support"""
    user = request.user_obj
    
    serializer = ComplaintSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return StandardError.validation_error(serializer.errors)
    
    data = serializer.validated_data
    title = data.get('title')
    description = data.get('description')
    location = data.get('location')
    
    try:
        with transaction.atomic():
            # Classify complaint using NLP (with multi-department support)
            nlp_result = classifier.classify_multi_department(description)
            complaint_id = generate_complaint_id()
            
            # Extract multi-department info
            primary_department = nlp_result['predictedDepartment']
            all_departments = nlp_result.get('departments', [primary_department])
            is_multi_routing = nlp_result.get('multiDepartmentRouting', False)
            
            # Create complaint
            complaint = Complaint.objects.create(
                id=complaint_id,
                user=user,
                title=title,
                description=description,
                location=location,
                status='Submitted',
                department=primary_department,
                primary_department=primary_department,
                departments=all_departments,
                priority=nlp_result['urgency'],
                confidence_score=nlp_result['confidenceScore'],
                nlp_analysis=nlp_result
            )
            
            # Create history entry
            ComplaintHistory.objects.create(
                complaint=complaint,
                user=user,
                action='Complaint Submitted',
                status_from=None,
                status_to='Submitted',
                comment=f'Complaint routed to: {", ".join(all_departments)}'
            )
            
            # Create notification with multi-department info
            dept_message = f'{len(all_departments)} departments' if is_multi_routing else primary_department
            Notification.objects.create(
                user=user,
                complaint=complaint,
                type='complaint_submitted',
                message=f'Your complaint {complaint_id} has been submitted and routed to {dept_message}'
            )
            
            response_data = {
                'id': complaint.id,
                'user_id': str(user.id),
                'title': complaint.title,
                'description': complaint.description,
                'location': complaint.location,
                'status': complaint.status,
                'department': complaint.department,
                'departments': all_departments,
                'primaryDepartment': primary_department,
                'multiDepartmentRouting': is_multi_routing,
                'priority': complaint.priority,
                'confidence_score': complaint.confidence_score,
                'nlp_analysis': complaint.nlp_analysis,
                'date_submitted': complaint.date_submitted.isoformat(),
                'date_updated': complaint.date_updated.isoformat(),
                'userName': user.name
            }
            
            return StandardError.success_response(
                data=response_data,
                message='Complaint submitted successfully',
                status_code=status.HTTP_201_CREATED
            )
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Error submitting complaint")
        return StandardError.server_error(
            message='Failed to submit complaint',
            details={'error': str(e)}
        )


@api_view(['GET'])
@require_auth
def get_complaints(request):
    """Get complaints based on user role"""
    user = request.user_obj
    
    try:
        if user.role == 'CITIZEN':
            complaints = Complaint.objects.filter(user=user).order_by('-date_submitted')
        elif user.role == 'OFFICER':
            complaints = Complaint.objects.filter(department=user.department).order_by('-date_submitted')
        else:  # ADMIN
            complaints = Complaint.objects.all().order_by('-date_submitted')
        
        # Serialize complaints
        result = []
        for complaint in complaints:
            data = {
                'id': complaint.id,
                'user_id': str(complaint.user.id),
                'userName': complaint.user.name,
                'title': complaint.title,
                'description': complaint.description,
                'location': complaint.location,
                'status': complaint.status,
                'department': complaint.department,
                'priority': complaint.priority,
                'confidence_score': complaint.confidence_score,
                'nlp_analysis': complaint.nlp_analysis,
                'date_submitted': complaint.date_submitted.isoformat(),
                'date_updated': complaint.date_updated.isoformat()
            }
            result.append(data)
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@require_auth
def get_complaint(request, complaint_id):
    """Get a single complaint by ID"""
    user = request.user_obj
    
    try:
        complaint = Complaint.objects.filter(id=complaint_id).first()
        if not complaint:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get history
        history = ComplaintHistory.objects.filter(complaint=complaint).order_by('-created_at')
        history_data = []
        for h in history:
            history_data.append({
                'id': h.id,
                'complaint_id': h.complaint.id,
                'user_id': str(h.user.id),
                'action': h.action,
                'status_from': h.status_from,
                'status_to': h.status_to,
                'comment': h.comment,
                'created_at': h.created_at.isoformat()
            })
        
        response_data = {
            'id': complaint.id,
            'user_id': str(complaint.user.id),
            'userName': complaint.user.name,
            'title': complaint.title,
            'description': complaint.description,
            'location': complaint.location,
            'status': complaint.status,
            'department': complaint.department,
            'priority': complaint.priority,
            'confidence_score': complaint.confidence_score,
            'nlp_analysis': complaint.nlp_analysis,
            'date_submitted': complaint.date_submitted.isoformat(),
            'date_updated': complaint.date_updated.isoformat(),
            'history': history_data,
            'attachments': []
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@require_auth
def update_status(request, complaint_id):
    """Update complaint status"""
    user = request.user_obj
    
    serializer = StatusUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    new_status = serializer.validated_data.get('status')
    comment = serializer.validated_data.get('comment', '')
    
    try:
        with transaction.atomic():
            complaint = Complaint.objects.filter(id=complaint_id).first()
            if not complaint:
                return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)
            
            old_status = complaint.status
            complaint.status = new_status
            complaint.save()
            
            # Create history entry
            ComplaintHistory.objects.create(
                complaint=complaint,
                user=user,
                action='Status Updated',
                status_from=old_status,
                status_to=new_status,
                comment=comment
            )
            
            # Create notification
            Notification.objects.create(
                user=complaint.user,
                complaint=complaint,
                type='status_updated',
                message=f'Your complaint {complaint_id} status has been updated to {new_status}'
            )
            
            response_data = {
                'id': complaint.id,
                'user_id': str(complaint.user.id),
                'title': complaint.title,
                'description': complaint.description,
                'location': complaint.location,
                'status': complaint.status,
                'department': complaint.department,
                'priority': complaint.priority,
                'confidence_score': complaint.confidence_score,
                'nlp_analysis': complaint.nlp_analysis,
                'date_submitted': complaint.date_submitted.isoformat(),
                'date_updated': complaint.date_updated.isoformat()
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@require_auth
def classify_text(request):
    """Classify text using NLP"""
    serializer = ClassifyTextSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    text = serializer.validated_data.get('text')
    
    try:
        result = classifier.classify(text)
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_departments(request):
    """Get all departments"""
    try:
        departments = Department.objects.all()
        # Return array of department names
        dept_names = [dept.name for dept in departments]
        return Response(dept_names, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@require_auth
def get_analytics(request):
    """Get analytics data"""
    try:
        complaints = Complaint.objects.all()
        
        total = complaints.count()
        pending = complaints.exclude(status__in=['Resolved', 'Closed']).count()
        resolved = complaints.filter(status='Resolved').count()
        
        # Calculate average resolution time
        resolved_complaints = complaints.filter(status='Resolved')
        if resolved_complaints.exists():
            total_time = 0
            count = 0
            for c in resolved_complaints:
                days = (c.date_updated - c.date_submitted).days
                total_time += days
                count += 1
            avg_days = total_time / count if count > 0 else 0
            avg_resolution_time = f"{avg_days:.1f} Days"
        else:
            avg_resolution_time = "N/A"
        
        return Response({
            'total': total,
            'pending': pending,
            'resolved': resolved,
            'avgResolutionTime': avg_resolution_time
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@require_auth
def get_notifications(request):
    """Get user notifications"""
    user = request.user_obj
    
    try:
        notifications = Notification.objects.filter(user=user).order_by('-created_at')[:50]
        
        result = []
        for n in notifications:
            result.append({
                'id': n.id,
                'user_id': str(n.user.id),
                'complaint_id': n.complaint.id,
                'type': n.type,
                'message': n.message,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat()
            })
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@require_auth
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    user = request.user_obj
    
    try:
        notification = Notification.objects.filter(id=notification_id, user=user).first()
        if notification:
            notification.is_read = True
            notification.save()
            return Response({'status': 'marked as read'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'GET'])
@require_auth
def create_officer(request):
    """Create a new officer user or get all users (Admin only)"""
    user = request.user_obj
    
    # Check if user is admin
    if user.role != 'ADMIN':
        return StandardError.permission_error('Only administrators can manage officer accounts')
    
    # GET - List all users
    if request.method == 'GET':
        try:
            users = User.objects.all().order_by('-created_at')
            users_data = [{
                'id': str(u.id),
                'email': u.email,
                'name': u.name,
                'role': u.role,
                'department': u.department,
                'phone': u.phone,
                'created_at': u.created_at.isoformat() if u.created_at else None
            } for u in users]
            
            return StandardError.success_response(data=users_data)
        except Exception as e:
            return StandardError.server_error(message='Failed to fetch users', details={'error': str(e)})
    
    # POST - Create officer
    data = request.data
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    department = data.get('department')
    phone = data.get('phone', '')
    
    # Validation
    if not all([email, password, name, department]):
        return StandardError.validation_error({'message': 'Email, password, name, and department are required'})
    
    # Check if user exists
    if User.objects.filter(email=email).exists():
        return StandardError.error_response(
            message='User with this email already exists',
            error_code='USER_EXISTS',
            status_code=status.HTTP_409_CONFLICT
        )
    
    try:
        # Hash password with bcrypt (12 rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        
        # Create officer
        officer = User.objects.create(
            email=email,
            password_hash=hashed,
            name=name,
            role='OFFICER',
            phone=phone,
            department=department
        )
        
        return StandardError.success_response(
            data={
                'id': str(officer.id),
                'email': officer.email,
                'name': officer.name,
                'role': officer.role,
                'department': officer.department,
                'phone': officer.phone
            },
            message='Officer created successfully',
            status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return StandardError.server_error(message='Failed to create officer', details={'error': str(e)})
