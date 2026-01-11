from rest_framework import serializers
from .models import User, Complaint, ComplaintHistory, Notification, Department


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'phone', 'department', 'created_at']
        read_only_fields = ['id', 'created_at']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


class ComplaintHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintHistory
        fields = ['id', 'complaint', 'user', 'action', 'status_from', 'status_to', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'complaint', 'type', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class ComplaintSerializer(serializers.ModelSerializer):
    userName = serializers.CharField(source='user.name', read_only=True)
    history = ComplaintHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Complaint
        fields = [
            'id', 'user_id', 'user', 'userName', 'title', 'description', 'location',
            'status', 'department', 'priority', 'confidence_score', 'nlp_analysis',
            'date_submitted', 'date_updated', 'history'
        ]
        read_only_fields = ['id', 'date_submitted', 'date_updated']


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    name = serializers.CharField(min_length=2, max_length=255)
    role = serializers.ChoiceField(choices=['CITIZEN', 'OFFICER', 'ADMIN'], default='CITIZEN')
    department = serializers.CharField(required=False, allow_blank=True, max_length=255)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    
    def validate_password(self, value):
        """Validate password strength"""
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ComplaintSubmitSerializer(serializers.Serializer):
    title = serializers.CharField(min_length=5, max_length=255)
    description = serializers.CharField(min_length=10, max_length=5000)
    location = serializers.CharField(min_length=3, max_length=255)


class StatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=50)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=1000)


class ClassifyTextSerializer(serializers.Serializer):
    text = serializers.CharField()
