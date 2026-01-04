import datetime
import re


def generate_complaint_id():
    """Generate unique complaint ID"""
    from .models import Complaint
    
    current_year = datetime.datetime.now().year
    
    try:
        last_complaint = Complaint.objects.order_by('-date_submitted').first()
        if last_complaint:
            match = re.search(r'-(\d+)$', last_complaint.id)
            if match:
                next_num = int(match.group(1)) + 1
            else:
                next_num = 1
        else:
            next_num = 1
    except:
        next_num = 1
    
    return f"SMG-{current_year}-{str(next_num).zfill(4)}"
