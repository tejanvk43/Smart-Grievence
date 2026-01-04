# Smart Griev - Django Backend

This is the Django backend for the Smart Griev complaint management system, migrated from Flask.

## Features

- **Django REST Framework** for API endpoints
- **SQLite** database (can be easily switched to PostgreSQL)
- **JWT Authentication** for secure user sessions
- **NLP-based Complaint Classification** using scikit-learn
- **CORS enabled** for frontend integration

## Project Structure

```
backend_django/
├── smart_griev/          # Django project settings
│   ├── settings.py       # Configuration
│   ├── urls.py          # Main URL routing
│   └── wsgi.py          # WSGI configuration
├── api/                 # Main API app
│   ├── models.py        # Database models
│   ├── views.py         # API views/endpoints
│   ├── serializers.py   # DRF serializers
│   ├── urls.py          # API URL routing
│   ├── auth.py          # JWT authentication utilities
│   ├── utils.py         # Helper functions
│   └── nlp_classifier.py # NLP classification logic
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend_django
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
```

### 4. Create .env File (Optional)

Create a `.env` file in the `backend_django` directory:

```env
SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Seed Database

```bash
python manage.py seed_db
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver 0.0.0.0:5000
```

The backend will be available at `http://localhost:5000/`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Complaints
- `POST /api/complaints/submit` - Submit new complaint
- `GET /api/complaints` - Get complaints (filtered by user role)
- `GET /api/complaints/<id>` - Get single complaint
- `PUT /api/complaints/<id>/status` - Update complaint status

### NLP
- `POST /api/nlp/classify` - Classify text using NLP

### Other
- `GET /api/departments` - Get all departments
- `GET /api/analytics` - Get analytics data
- `GET /api/notifications` - Get user notifications
- `PUT /api/notifications/<id>/read` - Mark notification as read
- `GET /api/health` - Health check

## Differences from Flask Version

1. **Django ORM** instead of raw SQLite queries
2. **Django REST Framework** for cleaner API structure
3. **Built-in admin panel** at `/admin`
4. **Better separation of concerns** with Django apps
5. **Migration system** for database schema changes
6. **More robust middleware** for CORS, authentication, etc.

## Production Deployment

For production, consider:

1. Change `DEBUG = False` in settings.py
2. Set a strong `SECRET_KEY` in environment variables
3. Use PostgreSQL instead of SQLite
4. Use gunicorn: `gunicorn smart_griev.wsgi:application`
5. Set proper `ALLOWED_HOSTS` in settings.py
6. Configure CORS properly (not allow all origins)

## Testing

Run tests with:

```bash
python manage.py test
```

## Admin Panel

Access the Django admin panel at `http://localhost:5000/admin/` after creating a superuser.
