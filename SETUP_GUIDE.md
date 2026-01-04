# Smart Griev - Complete Setup Guide

## Overview

Smart Griev is an AI-powered complaint management system with:
- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **Backend**: Django + Django REST Framework + SQLite
- **NLP**: scikit-learn for automatic department classification

## Quick Start

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.9+ (for backend)
- **pnpm** (for frontend package management)

### Option 1: Automated Setup (Recommended)

#### Windows

```bash
# Setup and run both frontend and backend
.\setup_and_run.bat
```

#### Linux/Mac

```bash
# Make script executable
chmod +x setup_and_run.sh

# Run setup
./setup_and_run.sh
```

### Option 2: Manual Setup

#### Frontend Setup

```bash
# Install frontend dependencies
pnpm install

# Start development server
pnpm dev
```

Frontend will be available at: `http://localhost:3000`

#### Backend Setup (Django)

```bash
# Navigate to Django backend
cd backend_django

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Seed database
python manage.py seed_db

# Start server
python manage.py runserver 0.0.0.0:5000
```

Backend will be available at: `http://localhost:5000`

## Fixed Issues

### Styling Issue on Windows

**Problem**: Styles wouldn't load when running on Windows.

**Cause**: The `index.html` file referenced a non-existent `index.css` file:
```html
<link rel="stylesheet" href="/index.css">
```

**Solution**: Removed the CSS link since TailwindCSS is loaded via CDN in the same HTML file. The project uses:
- TailwindCSS via CDN (`https://cdn.tailwindcss.com`)
- Inline style configuration in `index.html`
- Custom styles in `<style>` tag

This issue affected both Windows and Linux systems but was more noticeable on Windows.

## Architecture

### Frontend Structure
```
/
├── App.tsx                 # Main application component
├── index.tsx              # Entry point
├── index.html             # HTML template with TailwindCSS
├── components/            # Reusable components
│   ├── ComplaintCard.tsx
│   └── StatusBadge.tsx
├── pages/                 # Page components
│   ├── LandingPage.tsx
│   ├── CitizenDashboard.tsx
│   ├── OfficerDashboard.tsx
│   └── AdminDashboard.tsx
└── services/              # API services
    ├── api.ts
    └── mockApi.ts
```

### Backend Structure (Django)
```
backend_django/
├── smart_griev/           # Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api/                   # Main API app
│   ├── models.py          # Database models
│   ├── views.py           # API endpoints
│   ├── serializers.py     # DRF serializers
│   ├── auth.py            # JWT authentication
│   ├── nlp_classifier.py  # NLP classification
│   └── management/        # Custom commands
└── manage.py
```

## Migration from Flask to Django

The backend has been migrated from Flask to Django with the following improvements:

### Key Improvements

1. **Django ORM** - Better database abstraction and type safety
2. **Django REST Framework** - Cleaner API structure with serializers
3. **Built-in Admin Panel** - Easy data management at `/admin`
4. **Migration System** - Version-controlled database schema
5. **Better Testing** - Integrated testing framework
6. **Middleware Stack** - Better request/response handling

### API Compatibility

The Django backend maintains **100% API compatibility** with the Flask version:
- Same endpoints
- Same request/response formats
- Same JWT authentication
- Same NLP classification logic

### Breaking Changes

**None!** The frontend doesn't need any changes. Just point it to the Django backend.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Complaints
- `POST /api/complaints/submit` - Submit complaint
- `GET /api/complaints` - Get complaints
- `GET /api/complaints/<id>` - Get single complaint
- `PUT /api/complaints/<id>/status` - Update status

### Other
- `GET /api/departments` - Get departments
- `GET /api/analytics` - Get analytics
- `GET /api/notifications` - Get notifications
- `POST /api/nlp/classify` - Classify text
- `GET /api/health` - Health check

## Default Users

After setup, you can create test users:

### Citizen
```json
{
  "email": "citizen@test.com",
  "password": "password123",
  "name": "Test Citizen",
  "role": "CITIZEN"
}
```

### Officer
```json
{
  "email": "officer@test.com",
  "password": "password123",
  "name": "Test Officer",
  "role": "OFFICER",
  "department": "Public Works & Infrastructure"
}
```

### Admin
```json
{
  "email": "admin@test.com",
  "password": "password123",
  "name": "Test Admin",
  "role": "ADMIN"
}
```

## Environment Variables

### Backend (.env in backend_django/)
```env
SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
```

## Production Deployment

### Frontend
```bash
# Build for production
pnpm build

# Preview production build
pnpm preview
```

### Backend
```bash
# Collect static files
python manage.py collectstatic

# Run with gunicorn
gunicorn smart_griev.wsgi:application --bind 0.0.0.0:5000
```

## Troubleshooting

### Styles not loading
- **Issue**: CSS styles don't appear
- **Solution**: Clear browser cache and hard reload (Ctrl+Shift+R)
- **Verify**: TailwindCSS CDN link is present in `index.html`

### Backend won't start
- **Issue**: Django server fails to start
- **Solution**: 
  1. Ensure virtual environment is activated
  2. Run migrations: `python manage.py migrate`
  3. Check if port 5000 is available

### CORS errors
- **Issue**: Frontend can't connect to backend
- **Solution**: Ensure `django-cors-headers` is installed and configured in settings

## Support

For issues or questions:
1. Check [backend_django/README.md](backend_django/README.md) for backend details
2. Review error logs in terminal
3. Check browser console for frontend errors

## License

MIT License
