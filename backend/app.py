from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from nlp_classifier import classifier
import datetime
import re
import jwt
import uuid
import bcrypt
import json
from db import get_db_connection, init_db

app = Flask(__name__)
CORS(app)

# Initialize Database on Startup
init_db()

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
             
        # Convert sqlite row to dict for easier usage
        user_dict = dict(user)
        return user_dict, None
    except jwt.ExpiredSignatureError:
        return None, 'Token has expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'
    except Exception as e:
        return None, str(e)

def generate_complaint_id():
    current_year = datetime.datetime.now().year
    conn = get_db_connection()
    result = conn.execute('SELECT id FROM complaints ORDER BY date_submitted DESC LIMIT 1').fetchone()
    conn.close()

    try:
        if result:
            last_id = result['id']
            match = re.search(r'-(\d+)$', last_id)
            if match:
                next_num = int(match.group(1)) + 1
            else:
                next_num = 1
        else:
            next_num = 1
    except:
        next_num = 1

    return f"SMG-{current_year}-{str(next_num).zfill(4)}"

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Smart Griev Backend Running (SQLite)'}), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'CITIZEN')
    department = data.get('department')
    phone = data.get('phone', '')

    if not email or not password or not name:
        return jsonify({'error': 'Email, password, and name are required'}), 400

    conn = get_db_connection()
    try:
        # Check if user exists
        existing = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            return jsonify({'error': 'User already exists'}), 400

        user_id = str(uuid.uuid4())
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        dept_val = department if role == 'OFFICER' else None
        
        conn.execute(
            'INSERT INTO users (id, email, password_hash, name, role, phone, department) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user_id, email, hashed, name, role, phone, dept_val)
        )
        conn.commit()
        
        # Generate Token
        token = jwt.encode({
            'sub': user_id,
            'email': email,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, Config.SECRET_KEY, algorithm="HS256")

        return jsonify({
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'role': role,
                'department': dept_val
            },
            'session': {
                'access_token': token
            }
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    conn = get_db_connection()
    try:
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            token = jwt.encode({
                'sub': user['id'],
                'email': user['email'],
                'role': user['role'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
            }, Config.SECRET_KEY, algorithm="HS256")
            
            return jsonify({
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'phone': user['phone'],
                    'role': user['role'],
                    'department': user['department']
                },
                'session': {
                    'access_token': token
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/complaints/submit', methods=['POST'])
def submit_complaint():
    user, error = get_auth_user(request)
    if error:
        return jsonify({'error': error}), 401

    data = request.json
    title = data.get('title')
    description = data.get('description')
    location = data.get('location')

    if not title or not description or not location:
        return jsonify({'error': 'Title, description, and location are required'}), 400

    conn = get_db_connection()
    try:
        nlp_result = classifier.classify(description)
        complaint_id = generate_complaint_id()
        
        # User name is in user dict
        user_name = user['name']

        complaint_data = (
            complaint_id,
            user['id'],
            title,
            description,
            location,
            'Submitted',
            nlp_result['predictedDepartment'],
            nlp_result['urgency'],
            nlp_result['confidenceScore'],
            json.dumps(nlp_result),
            datetime.datetime.utcnow().isoformat(),
            datetime.datetime.utcnow().isoformat()
        )

        conn.execute('''
            INSERT INTO complaints (id, user_id, title, description, location, status, department, priority, confidence_score, nlp_analysis, date_submitted, date_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', complaint_data)

        # History
        history_data = (
            complaint_id,
            user['id'],
            'Complaint Submitted',
            None,
            'Submitted',
            'Initial complaint submission'
        )
        conn.execute('''
            INSERT INTO complaint_history (complaint_id, user_id, action, status_from, status_to, comment)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', history_data)

        # Notification
        notification_data = (
            user['id'],
            complaint_id,
            'complaint_submitted',
            f'Your complaint {complaint_id} has been submitted and routed to {nlp_result["predictedDepartment"]}'
        )
        conn.execute('''
            INSERT INTO notifications (user_id, complaint_id, type, message)
            VALUES (?, ?, ?, ?)
        ''', notification_data)
        
        conn.commit()

        # Construct response
        response_data = {
            'id': complaint_id,
            'user_id': user['id'],
            'title': title,
            'description': description,
            'location': location,
            'status': 'Submitted',
            'department': nlp_result['predictedDepartment'],
            'priority': nlp_result['urgency'],
            'confidence_score': nlp_result['confidenceScore'],
            'nlp_analysis': nlp_result,
            'date_submitted': complaint_data[10],
            'date_updated': complaint_data[11],
            'userName': user_name
        }

        return jsonify(response_data), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/complaints', methods=['GET'])
def get_complaints():
    user, error = get_auth_user(request)
    if error:
        return jsonify({'error': error}), 401
    
    conn = get_db_connection()
    try:
        user_role = user['role']
        user_department = user['department']

        if user_role == 'CITIZEN':
            cursor = conn.execute('SELECT * FROM complaints WHERE user_id = ? ORDER BY date_submitted DESC', (user['id'],))
        elif user_role == 'OFFICER':
            cursor = conn.execute('SELECT * FROM complaints WHERE department = ? ORDER BY date_submitted DESC', (user_department,))
        else:
            cursor = conn.execute('SELECT * FROM complaints ORDER BY date_submitted DESC')
            
        complaints = [dict(row) for row in cursor.fetchall()]

        # Attach user names and parse JSON
        for complaint in complaints:
            u = conn.execute('SELECT name FROM users WHERE id = ?', (complaint['user_id'],)).fetchone()
            complaint['userName'] = u['name'] if u else 'Unknown User'
            if complaint['nlp_analysis']:
                complaint['nlp_analysis'] = json.loads(complaint['nlp_analysis'])

        return jsonify(complaints), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/complaints/<complaint_id>', methods=['GET'])
def get_complaint(complaint_id):
    user, error = get_auth_user(request)
    if error:
        return jsonify({'error': error}), 401

    conn = get_db_connection()
    try:
        row = conn.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id,)).fetchone()
        if not row:
            return jsonify({'error': 'Complaint not found'}), 404
            
        complaint = dict(row)
        
        # User Name
        u = conn.execute('SELECT name FROM users WHERE id = ?', (complaint['user_id'],)).fetchone()
        complaint['userName'] = u['name'] if u else 'Unknown User'
        
        # Parse JSON
        if complaint['nlp_analysis']:
            complaint['nlp_analysis'] = json.loads(complaint['nlp_analysis'])
            
        # History
        h_rows = conn.execute('SELECT * FROM complaint_history WHERE complaint_id = ? ORDER BY created_at DESC', (complaint_id,)).fetchall()
        complaint['history'] = [dict(r) for r in h_rows]
        
        # Attachments (We don't have this table in schema yet, but logic was there, leaving empty list)
        complaint['attachments'] = [] # SQLite implementation simplified

        return jsonify(complaint), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/complaints/<complaint_id>/status', methods=['PUT'])
def update_status(complaint_id):
    user, error = get_auth_user(request)
    if error:
        return jsonify({'error': error}), 401

    data = request.json
    new_status = data.get('status')
    comment = data.get('comment', '')

    if not new_status:
        return jsonify({'error': 'Status is required'}), 400
        
    conn = get_db_connection()
    try:
        row = conn.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id,)).fetchone()
        if not row:
             return jsonify({'error': 'Complaint not found'}), 404
             
        old_status = row['status']
        user_id = row['user_id']
        
        updated_date = datetime.datetime.utcnow().isoformat()
        
        conn.execute('UPDATE complaints SET status = ?, date_updated = ? WHERE id = ?', (new_status, updated_date, complaint_id))
        
        # History
        conn.execute('''
            INSERT INTO complaint_history (complaint_id, user_id, action, status_from, status_to, comment)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (complaint_id, user['id'], 'Status Updated', old_status, new_status, comment))
        
        # Notification
        conn.execute('''
            INSERT INTO notifications (user_id, complaint_id, type, message)
            VALUES (?, ?, ?, ?)
        ''', (user_id, complaint_id, 'status_updated', f'Your complaint {complaint_id} status has been updated to {new_status}'))
        
        conn.commit()
        
        # Return updated complaint
        updated_row = conn.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id,)).fetchone()
        res = dict(updated_row)
        if res['nlp_analysis']:
            res['nlp_analysis'] = json.loads(res['nlp_analysis'])
            
        return jsonify(res), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/nlp/classify', methods=['POST'])
def classify_text():
    # Helper to test classifier without Auth if needed, but original had auth. usage
    # We will keep auth
    user, error = get_auth_user(request)
    if error:
        return jsonify({'error': error}), 401

    data = request.json
    text = data.get('text')

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    try:
        result = classifier.classify(text)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments', methods=['GET'])
def get_departments():
    conn = get_db_connection()
    try:
        rows = conn.execute('SELECT * FROM departments').fetchall()
        return jsonify([dict(r) for r in rows]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    user, error = get_auth_user(request)
    if error:
        return jsonify({'error': error}), 401
        
    conn = get_db_connection()
    try:
        rows = conn.execute('SELECT * FROM complaints').fetchall()
        complaints = [dict(r) for r in rows]
        
        total = len(complaints)
        pending = len([c for c in complaints if c['status'] not in ['Resolved', 'Closed']])
        resolved = len([c for c in complaints if c['status'] == 'Resolved'])
        
        if resolved > 0:
            total_time = 0
            count = 0
            for c in complaints:
                if c['status'] == 'Resolved':
                    # Parse dates
                    try:
                       submitted = datetime.datetime.fromisoformat(c['date_submitted'])
                       updated = datetime.datetime.fromisoformat(c['date_updated'])
                       days = (updated - submitted).days
                       total_time += days
                       count += 1
                    except:
                        pass # Valid isoformat expected
            avg_days = total_time / count if count > 0 else 0
            avg_resolution_time = f"{avg_days:.1f} Days"
        else:
            avg_resolution_time = "N/A"

        return jsonify({
            'total': total,
            'pending': pending,
            'resolved': resolved,
            'avgResolutionTime': avg_resolution_time
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    user, error = get_auth_user(request)
    if error:
        return jsonify({'error': error}), 401
        
    conn = get_db_connection()
    try:
        rows = conn.execute('SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50', (user['id'],)).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/notifications/<notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    user, error = get_auth_user(request)
    if error:
        return jsonify({'error': error}), 401
        
    conn = get_db_connection()
    try:
        conn.execute('UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?', (notification_id, user['id']))
        conn.commit()
        return jsonify({'status': 'marked as read'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
