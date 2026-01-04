from django.contrib import admin
from .models import User, Complaint, ComplaintHistory, Notification, Department

admin.site.register(User)
admin.site.register(Complaint)
admin.site.register(ComplaintHistory)
admin.site.register(Notification)
admin.site.register(Department)
