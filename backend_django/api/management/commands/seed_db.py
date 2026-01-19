from django.core.management.base import BaseCommand
from api.models import Department, User
import bcrypt


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
        
        # Create default admin user
        admin_email = 'admin@smartgriev.com'
        if not User.objects.filter(email=admin_email).exists():
            # Use same bcrypt rounds as registration (12)
            hashed = bcrypt.hashpw('Admin@123'.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
            User.objects.create(
                email=admin_email,
                password_hash=hashed,
                name='System Administrator',
                role='ADMIN',
                phone=''
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_email}'))
            self.stdout.write(self.style.SUCCESS('  Email: admin@smartgriev.com'))
            self.stdout.write(self.style.SUCCESS('  Password: Admin@123'))
        else:
            self.stdout.write(f'Admin user already exists: {admin_email}')
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
