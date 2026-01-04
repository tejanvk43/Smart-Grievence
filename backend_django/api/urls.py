from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health', views.health_check, name='health_check'),
    
    # Authentication
    path('auth/register', views.register, name='register'),
    path('auth/login', views.login, name='login'),
    
    # Complaints
    path('complaints/submit', views.submit_complaint, name='submit_complaint'),
    path('complaints', views.get_complaints, name='get_complaints'),
    path('complaints/<str:complaint_id>', views.get_complaint, name='get_complaint'),
    path('complaints/<str:complaint_id>/status', views.update_status, name='update_status'),
    
    # NLP
    path('nlp/classify', views.classify_text, name='classify_text'),
    
    # Departments
    path('departments', views.get_departments, name='get_departments'),
    
    # Analytics
    path('analytics', views.get_analytics, name='get_analytics'),
    
    # Notifications
    path('notifications', views.get_notifications, name='get_notifications'),
    path('notifications/<int:notification_id>/read', views.mark_notification_read, name='mark_notification_read'),
]
