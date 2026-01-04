from django.core.management.base import BaseCommand
from api.models import Department


class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Seed departments
        departments = [
            "Public Works & Infrastructure",
            "Water Supply & Sanitation",
            "Electricity & Power",
            "Transportation",
            "Health & Medical Services",
            "Education",
            "Police & Safety",
            "Revenue & Tax",
            "Environment & Pollution",
            "Consumer Affairs",
            "Others"
        ]
        
        for dept_name in departments:
            dept, created = Department.objects.get_or_create(name=dept_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created department: {dept_name}'))
            else:
                self.stdout.write(f'Department already exists: {dept_name}')
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
