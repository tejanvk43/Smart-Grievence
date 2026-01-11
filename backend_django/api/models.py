from django.db import models
import uuid


class User(models.Model):
    ROLE_CHOICES = [
        ('CITIZEN', 'Citizen'),
        ('OFFICER', 'Officer'),
        ('ADMIN', 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CITIZEN')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return f"{self.name} ({self.email})"


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    class Meta:
        db_table = 'departments'
    
    def __str__(self):
        return self.name


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    
    id = models.CharField(primary_key=True, max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Submitted', db_index=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    # Support multiple departments as JSON array
    departments = models.JSONField(default=list, blank=True, help_text="List of departments this complaint is routed to")
    primary_department = models.CharField(max_length=255, blank=True, null=True, help_text="Primary/main department")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, blank=True, null=True)
    confidence_score = models.FloatField(blank=True, null=True)
    # NLP analysis with multi-department routing info
    nlp_analysis = models.JSONField(blank=True, null=True)
    date_submitted = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'complaints'
        ordering = ['-date_submitted']
        indexes = [
            models.Index(fields=['user', '-date_submitted']),
            models.Index(fields=['status', '-date_submitted']),
            models.Index(fields=['primary_department', 'status']),
        ]
    
    def __str__(self):
        return f"{self.id} - {self.title}"
    
    def get_departments_list(self):
        """Get list of departments for this complaint"""
        if isinstance(self.departments, list):
            return self.departments
        return [self.primary_department] if self.primary_department else []


class ComplaintHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    status_from = models.CharField(max_length=50, blank=True, null=True)
    status_to = models.CharField(max_length=50, blank=True, null=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'complaint_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.complaint.id} - {self.action}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('complaint_submitted', 'Complaint Submitted'),
        ('status_updated', 'Status Updated'),
        ('comment_added', 'Comment Added'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} - {self.type}"
