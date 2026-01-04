# Flask vs Django - Backend Comparison

## Side-by-Side API Comparison

### Health Check Endpoint

#### Flask (backend/app.py)
```python
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Smart Griev Backend Running (SQLite)'}), 200
```

#### Django (backend_django/api/views.py)
```python
@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'ok',
        'message': 'Smart Griev Backend Running (Django + SQLite)'
    }, status=status.HTTP_200_OK)
```

---

### User Registration

#### Flask
```python
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    # ... validation
    
    conn = get_db_connection()
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn.execute('INSERT INTO users ...', (...))
        conn.commit()
        # ... return response
    finally:
        conn.close()
```

#### Django
```python
@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, ...)
    
    data = serializer.validated_data
    # ... validation already done by serializer
    
    user = User.objects.create(...)  # ORM - cleaner
    token = generate_token(user)
    return Response({...})
```

---

### Get Complaints

#### Flask
```python
@app.route('/api/complaints', methods=['GET'])
def get_complaints():
    user, error = get_auth_user(request)
    if error:
        return jsonify({'error': error}), 401
    
    conn = get_db_connection()
    try:
        if user_role == 'CITIZEN':
            cursor = conn.execute('SELECT * FROM complaints WHERE user_id = ?', (user['id'],))
        # ... more SQL queries
        complaints = [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
```

#### Django
```python
@api_view(['GET'])
@require_auth
def get_complaints(request):
    user = request.user_obj  # Already authenticated
    
    if user.role == 'CITIZEN':
        complaints = Complaint.objects.filter(user=user).order_by('-date_submitted')
    # ... ORM queries - type-safe, cleaner
    
    return Response([...])
```

---

## Database Comparison

### Flask - Raw SQL

```python
# db.py
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Creating tables
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        ...
    )
''')

# Querying
conn.execute('SELECT * FROM complaints WHERE user_id = ?', (user_id,))
```

### Django - ORM

```python
# models.py
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    # ...
    
    class Meta:
        db_table = 'users'

# Migrations (auto-generated)
python manage.py makemigrations
python manage.py migrate

# Querying (type-safe)
User.objects.filter(email=email).first()
Complaint.objects.filter(user=user).order_by('-date_submitted')
```

---

## Authentication Comparison

### Flask

```python
def get_auth_user(req):
    auth_header = req.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, 'Missing or invalid authorization header'
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (payload['sub'],)).fetchone()
        conn.close()
        
        if not user:
            return None, 'User not found'
        
        user_dict = dict(user)
        return user_dict, None
    except jwt.ExpiredSignatureError:
        return None, 'Token has expired'
    # ...

# Usage in route
@app.route('/api/complaints', methods=['GET'])
def get_complaints():
    user, error = get_auth_user(request)
    if error:
        return jsonify({'error': error}), 401
    # ... rest of code
```

### Django

```python
# auth.py
def get_auth_user(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    # ... similar logic but cleaner
    
    user = User.objects.filter(id=payload['sub']).first()  # ORM
    return user, None

def require_auth(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        user, error = get_auth_user(request)
        if error:
            return Response({'error': error}, status=401)
        request.user_obj = user
        return f(request, *args, **kwargs)
    return decorated_function

# Usage in view
@api_view(['GET'])
@require_auth  # Decorator - cleaner
def get_complaints(request):
    user = request.user_obj  # Already authenticated
    # ... rest of code
```

---

## Validation Comparison

### Flask - Manual

```python
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not email or not password or not name:
        return jsonify({'error': 'Email, password, and name are required'}), 400
    
    # More validation...
```

### Django - Serializers

```python
# serializers.py
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()  # Auto-validates email format
    password = serializers.CharField(write_only=True)
    name = serializers.CharField()
    role = serializers.ChoiceField(choices=['CITIZEN', 'OFFICER', 'ADMIN'])
    # ...

# views.py
@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():  # All validation done here
        return Response({'error': serializer.errors}, ...)
    
    data = serializer.validated_data  # Already validated!
```

---

## Error Handling

### Flask

```python
try:
    # database operations
    conn.commit()
except Exception as e:
    conn.rollback()
    return jsonify({'error': str(e)}), 500
finally:
    conn.close()
```

### Django

```python
try:
    with transaction.atomic():  # Auto-rollback on error
        # database operations
        complaint.save()
        # ...
except Exception as e:
    return Response({'error': str(e)}), status=500
# No need for finally - Django handles connections
```

---

## Admin Interface

### Flask
**No built-in admin** - Would need to:
- Build custom admin UI
- Create CRUD endpoints
- Handle authentication
- Build forms
- Add search/filtering

### Django
**Built-in admin panel:**

```python
# admin.py
from django.contrib import admin
from .models import User, Complaint

admin.site.register(User)
admin.site.register(Complaint)
```

Access at `/admin` with superuser credentials:
- CRUD operations
- Search and filtering
- Inline editing
- Export data
- Custom actions

---

## Testing

### Flask

```python
# No built-in test framework
# Would use pytest or unittest manually

def test_register():
    # Setup test client
    # Make request
    # Assert response
    pass
```

### Django

```python
# Built-in test framework
from django.test import TestCase
from rest_framework.test import APITestCase

class UserTests(APITestCase):
    def test_register(self):
        response = self.client.post('/api/auth/register', {
            'email': 'test@test.com',
            'password': 'pass123',
            'name': 'Test User'
        })
        self.assertEqual(response.status_code, 201)

# Run tests
# python manage.py test
```

---

## Deployment

### Flask

```python
# Run with gunicorn
gunicorn app:app --bind 0.0.0.0:5000

# Manual setup needed for:
# - Static files
# - Database migrations
# - Environment config
```

### Django

```python
# Run with gunicorn
gunicorn smart_griev.wsgi:application --bind 0.0.0.0:5000

# Built-in support for:
# - Static files: python manage.py collectstatic
# - Migrations: python manage.py migrate
# - Environment: settings.py with env vars
```

---

## Pros and Cons

### Flask Advantages
✅ Lightweight and minimal
✅ Faster for very simple APIs
✅ More flexible (less opinionated)
✅ Easier to learn basics

### Flask Disadvantages
❌ More boilerplate code
❌ Manual SQL queries
❌ No built-in admin
❌ No ORM by default
❌ Manual validation
❌ Less structure

### Django Advantages
✅ Powerful ORM
✅ Built-in admin panel
✅ DRF for REST APIs
✅ Built-in validation
✅ Migration system
✅ Better security out-of-box
✅ Excellent documentation
✅ Scalable structure

### Django Disadvantages
❌ Steeper learning curve
❌ More "magic" (less explicit)
❌ Heavier framework
❌ More opinionated

---

## Performance Comparison

For Smart Griev scale:
- **Flask**: Slightly faster for simple requests (< 5ms difference)
- **Django**: Better for complex queries with joins
- **Both**: More than adequate for < 10k users

The performance difference is negligible for this application.

---

## Recommendation

**For Smart Griev, Django is better because:**

1. **Built-in Admin** - Easy data management
2. **ORM** - Safer, cleaner database operations
3. **Validation** - DRF serializers reduce code
4. **Scalability** - Easier to add features
5. **Community** - Larger ecosystem
6. **Security** - Better defaults

**Use Flask if:**
- Building microservices
- Need ultra-lightweight
- Prefer explicit over implicit
- Don't need admin panel

**For this project: Django wins** 🏆
