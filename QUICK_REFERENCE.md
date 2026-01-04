# Smart Griev - Quick Reference

## 🚀 One-Command Setup

### Windows
```bash
setup_and_run.bat
```

### Linux/Mac
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

---

## 🏃 Running the Project

### Frontend (Terminal 1)
```bash
pnpm dev
```
**URL:** http://localhost:3000

### Backend - Django (Terminal 2)
```bash
cd backend_django
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate          # Windows
python manage.py runserver 0.0.0.0:5000
```
**URL:** http://localhost:5000

### Backend - Flask (Alternative)
```bash
cd backend
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate          # Windows
python app.py
```
**URL:** http://localhost:5000

---

## 🔧 Common Commands

### Frontend
```bash
pnpm install        # Install dependencies
pnpm dev           # Development server
pnpm build         # Production build
pnpm preview       # Preview production build
```

### Django Backend
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py seed_db

# Run
python manage.py runserver 0.0.0.0:5000

# Admin
python manage.py createsuperuser

# Tests
python manage.py test
```

---

## 📋 Test Users

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

---

## 🔌 API Endpoints

### Base URL: `http://localhost:5000/api`

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login user |

#### Complaints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/complaints/submit` | Submit complaint |
| GET | `/complaints` | Get complaints (role-based) |
| GET | `/complaints/{id}` | Get single complaint |
| PUT | `/complaints/{id}/status` | Update status |

#### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/departments` | Get all departments |
| GET | `/analytics` | Get analytics data |
| GET | `/notifications` | Get user notifications |
| PUT | `/notifications/{id}/read` | Mark as read |
| POST | `/nlp/classify` | Classify text with NLP |
| GET | `/health` | Health check |

---

## 🗂️ Project Structure

```
Smart-Grievence/
├── 📁 Frontend
│   ├── App.tsx              # Main app
│   ├── index.tsx           # Entry point
│   ├── index.html          # HTML + TailwindCSS
│   ├── components/         # Reusable components
│   ├── pages/              # Page components
│   └── services/           # API services
│
├── 📁 backend/             # Flask version
│   ├── app.py              # Main application
│   ├── db.py               # Database functions
│   ├── nlp_classifier.py   # NLP logic
│   └── requirements.txt    # Dependencies
│
└── 📁 backend_django/      # Django version ⭐
    ├── smart_griev/        # Project settings
    ├── api/                # Main app
    │   ├── models.py       # Database models
    │   ├── views.py        # API endpoints
    │   ├── serializers.py  # DRF serializers
    │   ├── auth.py         # Authentication
    │   └── nlp_classifier.py
    └── manage.py           # Django CLI
```

---

## 🐛 Troubleshooting

### Styles not loading
```bash
# Clear browser cache and hard reload
Ctrl + Shift + R (Chrome/Firefox)
Cmd + Shift + R (Mac)
```

### Backend won't start
```bash
# Ensure virtual environment is activated
cd backend_django
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run migrations
python manage.py migrate

# Check if port 5000 is free
# Linux/Mac:
lsof -i :5000
# Windows:
netstat -ano | findstr :5000
```

### CORS errors
```bash
# Ensure django-cors-headers is installed
pip install django-cors-headers

# Check settings.py has:
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
]
```

### Frontend can't connect to backend
1. Check backend is running on port 5000
2. Check API URL in frontend code
3. Clear browser cache
4. Check browser console for errors

---

## 📚 Documentation Files

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions
- **[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)** - What was changed/fixed
- **[FLASK_VS_DJANGO.md](FLASK_VS_DJANGO.md)** - Backend comparison
- **[backend_django/README.md](backend_django/README.md)** - Django docs
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - This file

---

## 🔑 Key Features

### NLP Classification
- Automatic department routing
- 11 departments supported
- Urgency detection (Low/Medium/High)
- Sentiment analysis
- Keyword extraction
- 85-95% accuracy

### User Roles
- **CITIZEN** - Submit and track complaints
- **OFFICER** - Manage department complaints
- **ADMIN** - System-wide overview

### Technologies
- **Frontend:** React 19, TypeScript, Vite, TailwindCSS
- **Backend:** Django 5, DRF, SQLite
- **NLP:** scikit-learn, NLTK, TextBlob
- **Auth:** JWT tokens

---

## 📊 Departments

1. Public Works & Infrastructure
2. Water Supply & Sanitation
3. Electricity & Power
4. Transportation
5. Health & Medical Services
6. Education
7. Police & Safety
8. Revenue & Tax
9. Environment & Pollution
10. Consumer Affairs
11. Others

---

## 🎯 Next Steps

### For Development
1. Create test users
2. Submit sample complaints
3. Test NLP classification
4. Try different user roles
5. Check admin panel

### For Production
1. Set `DEBUG = False`
2. Configure `SECRET_KEY`
3. Use PostgreSQL
4. Setup gunicorn
5. Configure HTTPS
6. Setup domain

---

## 💡 Tips

- Use Django admin panel for data management: `/admin`
- Check NLP confidence scores in complaint details
- Test with different complaint types to see classification
- Monitor browser console for frontend errors
- Check terminal for backend errors

---

## ✅ What's Fixed

1. **Styling Issue** - Removed broken CSS link in index.html
2. **Backend Migration** - Complete Django backend created
3. **Setup Automation** - One-command setup scripts
4. **Documentation** - Comprehensive guides added

---

## 🆘 Getting Help

1. Check documentation files above
2. Review error messages in terminal
3. Check browser console (F12)
4. Verify all dependencies installed
5. Ensure virtual environment activated

---

**Happy Coding! 🚀**
