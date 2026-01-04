# Quick Setup & Test Guide

## Initial Setup

### 1. Backend Setup
```bash
cd backend_django
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_db
python manage.py runserver
```

### 2. Frontend Setup (in new terminal)
```bash
pnpm install
pnpm dev
```

## Default Credentials

### Admin User (Pre-seeded)
- **Email**: `admin@smartgriev.com`
- **Password**: `Admin@123`
- **Access**: Full system control, can create officers

## Testing New Features

### 1. Test Registration Restrictions
1. Go to landing page
2. Try to register - you'll see role selector is disabled
3. Register as citizen (only option)
4. Try to manually send POST with OFFICER/ADMIN role - should get 403 error

### 2. Test Admin Login & Officer Creation
1. Login with admin credentials above
2. You'll be redirected to Admin Dashboard
3. Click "Create Officer" button (top right)
4. Fill in officer details:
   - Name: Test Officer
   - Email: officer@test.com
   - Password: Officer@123
   - Department: Select from dropdown
   - Phone: (optional)
5. Click "Create Officer"
6. Should see success message and modal closes

### 3. Test Officer Login
1. Logout from admin
2. Login with newly created officer credentials
3. Should redirect to Officer Dashboard
4. Officer can only see complaints from their department

### 4. Test Department Endpoint
```bash
# Should return array of strings
curl http://localhost:8000/api/departments
```

Expected output:
```json
[
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
```

## Common Issues & Solutions

### Issue: Database not seeded
**Solution**: 
```bash
python manage.py seed_db
```

### Issue: Admin user already exists error
**Solution**: This is normal - admin only created once

### Issue: Cannot create officer
**Solution**: 
- Check you're logged in as admin
- Check JWT token in browser localStorage
- Check backend server is running

### Issue: Departments not loading in dropdown
**Solution**:
- Verify backend running on port 8000
- Check browser console for CORS errors
- Verify `/api/departments` endpoint returns data

## File Structure Reference

```
backend_django/
├── api/
│   ├── views.py (✓ Modified - added create_officer, updated register & departments)
│   ├── urls.py (✓ Modified - added admin/users route)
│   └── management/commands/
│       └── seed_db.py (✓ Modified - added admin user creation)
└── .gitignore (✓ Modified - removed *.db exclusion)

pages/
├── AdminDashboard.tsx (✓ Modified - added officer creation UI)
└── LandingPage.tsx (✓ Modified - disabled role selector for registration)

services/
└── api.ts (✓ Modified - added createOfficer method)
```

## API Endpoints Quick Reference

### Public Endpoints
- `POST /api/auth/register` - Register citizen only
- `POST /api/auth/login` - Login (all roles)
- `GET /api/departments` - Get department list

### Protected Endpoints (Require JWT)
- `POST /api/complaints/submit` - Submit complaint
- `GET /api/complaints` - Get complaints
- `GET /api/analytics` - Get statistics

### Admin-Only Endpoints
- `POST /api/admin/users` - Create officer account

## Environment Variables

Create `.env` file in `backend_django/`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_NAME=db.sqlite3
```

## Database Seed Data

### Departments (11 total)
All departments are automatically seeded on first run

### Users
- 1 Admin user (admin@smartgriev.com)
- Officers created via admin panel
- Citizens self-register

## Development Workflow

1. **Start Backend**: `cd backend_django && python manage.py runserver`
2. **Start Frontend**: `pnpm dev` (in new terminal)
3. **Access App**: http://localhost:5173
4. **API Docs**: Backend runs on http://localhost:8000

## Production Deployment

1. Set `DEBUG=False` in settings
2. Update `ALLOWED_HOSTS`
3. Use production database (PostgreSQL recommended)
4. Set strong `SECRET_KEY`
5. Run `python manage.py collectstatic`
6. Use gunicorn: `gunicorn smart_griev.wsgi:application`
