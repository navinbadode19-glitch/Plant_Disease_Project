import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agri_guard.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            language TEXT DEFAULT 'English',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create history table to track diagnoses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            crop_type TEXT NOT NULL,
            disease_name TEXT NOT NULL,
            severity TEXT NOT NULL,
            confidence REAL NOT NULL,
            image_path TEXT NOT NULL,
            symptoms TEXT,
            cause TEXT,
            chemical_treatment TEXT,
            organic_treatment TEXT,
            recovery_time TEXT,
            prevention TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Remove old 'admin' user if it exists
    cursor.execute('DELETE FROM users WHERE username = ?', ('admin',))
    
    # Seed default admin user 'nb' if not exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('nb',))
    if not cursor.fetchone():
        hashed_pwd = generate_password_hash('nbadmin')
        cursor.execute(
            'INSERT INTO users (username, password, language) VALUES (?, ?, ?)',
            ('nb', hashed_pwd, 'English')
        )
    
    conn.commit()
    conn.close()
    print("[Database] SQLite database initialized successfully!")

def register_user(username, password, preferred_lang='English'):
    hashed_pwd = generate_password_hash(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password, language) VALUES (?, ?, ?)',
            (username, hashed_pwd, preferred_lang)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"success": True, "user_id": user_id}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "message": "Username already exists."}
    except Exception as e:
        conn.close()
        return {"success": False, "message": str(e)}

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return {
            "id": user['id'],
            "username": user['username'],
            "language": user['language']
        }
    return None

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            "id": user['id'],
            "username": user['username'],
            "language": user['language']
        }
    return None

def update_user_language(user_id, language):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET language = ? WHERE id = ?', (language, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Database] Error updating language: {e}")
        conn.close()
        return False

def add_history_record(user_id, crop_type, disease_name, severity, confidence, image_path,
                       symptoms=None, cause=None, chemical_treatment=None,
                       organic_treatment=None, recovery_time=None, prevention=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO history (
                user_id, crop_type, disease_name, severity, confidence, image_path,
                symptoms, cause, chemical_treatment, organic_treatment, recovery_time, prevention
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, crop_type, disease_name, severity, confidence, image_path,
            symptoms, cause, chemical_treatment, organic_treatment, recovery_time, prevention
        ))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    except Exception as e:
        print(f"[Database] Error saving diagnosis history: {e}")
        conn.close()
        return None

def get_user_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    history_list = []
    for row in rows:
        history_list.append({
            "id": row["id"],
            "crop_type": row["crop_type"],
            "disease_name": row["disease_name"],
            "severity": row["severity"],
            "confidence": row["confidence"],
            "image_path": row["image_path"],
            "symptoms": row["symptoms"],
            "cause": row["cause"],
            "chemical_treatment": row["chemical_treatment"],
            "organic_treatment": row["organic_treatment"],
            "recovery_time": row["recovery_time"],
            "prevention": row["prevention"],
            "created_at": row["created_at"]
        })
    return history_list
