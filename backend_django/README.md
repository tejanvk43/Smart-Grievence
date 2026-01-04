# Django Backend

Production-ready Django backend with NLP complaint classification.

## Setup

```bash
cd backend_django
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_db
python manage.py runserver
```

**Admin credentials:** admin@smartgriev.com / Admin@123

## Project Structure

```
api/
├── models.py        # Database models
├── views.py         # API endpoints  
├── serializers.py   # Request/response validation
├── auth.py          # JWT authentication
└── nlp_classifier.py # NLP logic
```

## API Endpoints

**Auth**
- POST `/api/auth/register` - Register (citizens only)
- POST `/api/auth/login` - Login

**Complaints**
- POST `/api/complaints/submit` - Submit complaint
- GET `/api/complaints` - Get complaints
- PUT `/api/complaints/{id}/status` - Update status

**Admin**
- POST `/api/admin/users` - Create officer

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
