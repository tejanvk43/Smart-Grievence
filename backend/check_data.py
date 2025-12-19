import sqlite3
import json

def check_data():
    conn = sqlite3.connect('smart_griev.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    print("--- Users ---")
    users = c.execute('SELECT id, name, email, role, department FROM users').fetchall()
    for u in users:
        print(dict(u))
        
    print("\n--- Complaints ---")
    complaints = c.execute('SELECT id, title, department, status, user_id FROM complaints').fetchall()
    for comp in complaints:
        print(dict(comp))

    conn.close()

if __name__ == "__main__":
    check_data()
