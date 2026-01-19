from django.core.management.base import BaseCommand
from api.models import User
import bcrypt


class Command(BaseCommand):
    help = 'Reset admin user password'

    def handle(self, *args, **kwargs):
        admin_email = 'admin@smartgriev.com'
        
        try:
            # Delete existing admin if exists
            User.objects.filter(email=admin_email).delete()
            self.stdout.write(self.style.WARNING('Deleted existing admin user'))
            
            # Create fresh admin user with correct password hash
            hashed = bcrypt.hashpw('Admin@123'.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
            User.objects.create(
                email=admin_email,
                password_hash=hashed,
                name='System Administrator',
                role='ADMIN',
                phone=''
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Admin user created successfully!'))
            self.stdout.write(self.style.SUCCESS('  Email: admin@smartgriev.com'))
            self.stdout.write(self.style.SUCCESS('  Password: Admin@123'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
