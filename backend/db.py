import sqlite3
import datetime
import json
import os

DB_NAME = "smart_griev.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'CITIZEN',
            phone TEXT,
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Complaints table
    c.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Submitted',
            department TEXT,
            priority TEXT,
            confidence_score REAL,
            nlp_analysis TEXT, -- JSON string
            date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Complaint History table
    c.execute('''
        CREATE TABLE IF NOT EXISTS complaint_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            status_from TEXT,
            status_to TEXT,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (complaint_id) REFERENCES complaints (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Notifications table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            complaint_id TEXT NOT NULL,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (complaint_id) REFERENCES complaints (id)
        )
    ''')

    # Departments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Seed departments if empty
    c.execute('SELECT count(*) FROM departments')
    if c.fetchone()[0] == 0:
        depts = [
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
        for dept in depts:
            c.execute('INSERT INTO departments (name) VALUES (?)', (dept,))

    conn.commit()
    conn.close()
