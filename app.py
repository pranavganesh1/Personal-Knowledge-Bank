from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Change to your MySQL username
app.config['MYSQL_PASSWORD'] = 'admin'  # Change to your MySQL password
app.config['MYSQL_DB'] = 'pkb1'

mysql = MySQL(app)

# Helper function to get current user
def get_current_user():
    return session.get('user_id', 1)  # Default to user 1 for demo

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/notes')
def get_notes():
    user_id = get_current_user()
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT n.note_id, n.title, n.content, n.is_public, n.created_at, n.updated_at,
               c.name as category_name, nb.title as notebook_title,
               GROUP_CONCAT(DISTINCT t.name) as tags,
               (SELECT COUNT(*) FROM bookmark b WHERE b.note_id = n.note_id AND b.user_id = %s) as is_bookmarked
        FROM note n
        LEFT JOIN category c ON n.category_id = c.category_id
        LEFT JOIN notebook nb ON n.notebook_id = nb.notebook_id
        LEFT JOIN note_tag nt ON n.note_id = nt.note_id
        LEFT JOIN tag t ON nt.tag_id = t.tag_id
        GROUP BY n.note_id
        ORDER BY n.updated_at DESC
    """, (user_id,))
    notes = cur.fetchall()
    cur.close()
    
    notes_list = []
    for note in notes:
        notes_list.append({
            'note_id': note[0],
            'title': note[1],
            'content': note[2],
            'is_public': note[3],
            'created_at': note[4].strftime('%Y-%m-%d %H:%M'),
            'updated_at': note[5].strftime('%Y-%m-%d %H:%M'),
            'category': note[6],
            'notebook': note[7],
            'tags': note[8].split(',') if note[8] else [],
            'is_bookmarked': bool(note[9])
        })
    
    return jsonify(notes_list)

@app.route('/api/notes/<int:note_id>')
def get_note(note_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT n.note_id, n.title, n.content, n.is_public, n.created_at, n.updated_at,
               c.name as category_name, c.category_id, nb.title as notebook_title, nb.notebook_id,
               GROUP_CONCAT(DISTINCT t.name) as tags
        FROM note n
        LEFT JOIN category c ON n.category_id = c.category_id
        LEFT JOIN notebook nb ON n.notebook_id = nb.notebook_id
        LEFT JOIN note_tag nt ON n.note_id = nt.note_id
        LEFT JOIN tag t ON nt.tag_id = t.tag_id
        WHERE n.note_id = %s
        GROUP BY n.note_id
    """, (note_id,))
    note = cur.fetchone()
    cur.close()
    
    if note:
        return jsonify({
            'note_id': note[0],
            'title': note[1],
            'content': note[2],
            'is_public': note[3],
            'created_at': note[4].strftime('%Y-%m-%d %H:%M'),
            'updated_at': note[5].strftime('%Y-%m-%d %H:%M'),
            'category': note[6],
            'category_id': note[7],
            'notebook': note[8],
            'notebook_id': note[9],
            'tags': note[10].split(',') if note[10] else []
        })
    return jsonify({'error': 'Note not found'}), 404

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.json
    user_id = get_current_user()
    
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO note (user_id, title, content, is_public, category_id, notebook_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, data['title'], data['content'], data.get('is_public', 0), 
          data.get('category_id'), data.get('notebook_id')))
    
    note_id = cur.lastrowid
    
    # Add tags (this will trigger trg_auto_todo_reminder if 'todo' tag is added)
    if 'tags' in data and data['tags']:
        for tag_name in data['tags']:
            cur.execute("INSERT IGNORE INTO tag (name) VALUES (%s)", (tag_name,))
            cur.execute("SELECT tag_id FROM tag WHERE name = %s", (tag_name,))
            tag_id = cur.fetchone()[0]
            cur.execute("INSERT INTO note_tag (note_id, tag_id) VALUES (%s, %s)", (note_id, tag_id))
    
    mysql.connection.commit()
    cur.close()
    
    return jsonify({'note_id': note_id, 'message': 'Note created successfully'})

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.json
    
    cur = mysql.connection.cursor()
    # This UPDATE will trigger trg_note_version and trg_notebook_updated
    cur.execute("""
        UPDATE note 
        SET title = %s, content = %s, is_public = %s
        WHERE note_id = %s
    """, (data['title'], data['content'], data.get('is_public', 0), note_id))
    
    mysql.connection.commit()
    cur.close()
    
    return jsonify({'message': 'Note updated successfully'})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM note WHERE note_id = %s", (note_id,))
    mysql.connection.commit()
    cur.close()
    
    return jsonify({'message': 'Note deleted successfully'})

# ========== NEW: Note History (from trg_note_version trigger) ==========
@app.route('/api/notes/<int:note_id>/history')
def get_note_history(note_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT nh.history_id, nh.title_snapshot, nh.content_snapshot, 
               nh.version_at, u.name as edited_by
        FROM note_history nh
        LEFT JOIN app_user u ON nh.edited_by = u.user_id
        WHERE nh.note_id = %s
        ORDER BY nh.version_at DESC
    """, (note_id,))
    history = cur.fetchall()
    cur.close()
    
    return jsonify([{
        'history_id': h[0],
        'title': h[1],
        'content': h[2],
        'version_at': h[3].strftime('%Y-%m-%d %H:%M:%S'),
        'edited_by': h[4]
    } for h in history])

# ========== PROCEDURE: suggest_tag ==========
@app.route('/api/notes/<int:note_id>/suggest-tag', methods=['POST'])
def suggest_tag_for_note(note_id):
    data = request.json
    tag_id = data['tag_id']
    confidence = data.get('confidence', 0.75)
    
    cur = mysql.connection.cursor()
    cur.callproc('suggest_tag', [note_id, tag_id, confidence])
    mysql.connection.commit()
    cur.close()
    
    return jsonify({'message': 'Tag suggested successfully'})

@app.route('/api/notes/<int:note_id>/tag-suggestions')
def get_tag_suggestions(note_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT ts.suggestion_id, t.tag_id, t.name, ts.confidence, ts.suggested_at
        FROM tag_suggestion ts
        JOIN tag t ON ts.tag_id = t.tag_id
        WHERE ts.note_id = %s
        ORDER BY ts.confidence DESC
    """, (note_id,))
    suggestions = cur.fetchall()
    cur.close()
    
    return jsonify([{
        'suggestion_id': s[0],
        'tag_id': s[1],
        'tag_name': s[2],
        'confidence': float(s[3]),
        'suggested_at': s[4].strftime('%Y-%m-%d %H:%M')
    } for s in suggestions])

# ========== PROCEDURE: share_note (Collaboration) ==========
@app.route('/api/notes/<int:note_id>/share', methods=['POST'])
def share_note(note_id):
    data = request.json
    shared_with_user_id = data['user_id']
    access_level = data.get('access_level', 'read')
    
    cur = mysql.connection.cursor()
    cur.callproc('share_note', [note_id, shared_with_user_id, access_level])
    mysql.connection.commit()
    cur.close()
    
    return jsonify({'message': 'Note shared successfully'})

@app.route('/api/notes/<int:note_id>/collaborators')
def get_collaborators(note_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.collab_id, u.user_id, u.name, u.email, c.access_level, c.shared_at
        FROM collaboration c
        JOIN app_user u ON c.shared_with_user_id = u.user_id
        WHERE c.note_id = %s
    """, (note_id,))
    collabs = cur.fetchall()
    cur.close()
    
    return jsonify([{
        'collab_id': c[0],
        'user_id': c[1],
        'name': c[2],
        'email': c[3],
        'access_level': c[4],
        'shared_at': c[5].strftime('%Y-%m-%d %H:%M')
    } for c in collabs])

# ========== PROCEDURE: mark_reminder_done ==========
@app.route('/api/reminders/<int:reminder_id>/done', methods=['POST'])
def mark_reminder_done(reminder_id):
    cur = mysql.connection.cursor()
    cur.callproc('mark_reminder_done', [reminder_id])
    mysql.connection.commit()
    cur.close()
    
    return jsonify({'message': 'Reminder marked as done'})

# ========== Other existing routes ==========
@app.route('/api/categories')
def get_categories():
    cur = mysql.connection.cursor()
    cur.execute("SELECT category_id, name, description FROM category")
    categories = cur.fetchall()
    cur.close()
    
    return jsonify([{'id': c[0], 'name': c[1], 'description': c[2]} for c in categories])

@app.route('/api/notebooks')
def get_notebooks():
    user_id = get_current_user()
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT notebook_id, title, description, created_at 
        FROM notebook 
        WHERE user_id = %s
    """, (user_id,))
    notebooks = cur.fetchall()
    cur.close()
    
    return jsonify([{
        'id': n[0], 
        'title': n[1], 
        'description': n[2],
        'created_at': n[3].strftime('%Y-%m-%d %H:%M')
    } for n in notebooks])

@app.route('/api/users')
def get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id, name, email FROM app_user")
    users = cur.fetchall()
    cur.close()
    
    return jsonify([{'id': u[0], 'name': u[1], 'email': u[2]} for u in users])

@app.route('/api/tags')
def get_tags():
    cur = mysql.connection.cursor()
    cur.execute("SELECT tag_id, name FROM tag")
    tags = cur.fetchall()
    cur.close()
    
    return jsonify([{'id': t[0], 'name': t[1]} for t in tags])

@app.route('/api/reminders')
def get_reminders():
    user_id = get_current_user()
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.reminder_id, r.reminder_text, r.due_date, r.status, n.title, n.note_id
        FROM reminder r
        JOIN note n ON r.note_id = n.note_id
        WHERE r.user_id = %s
        ORDER BY r.due_date ASC
    """, (user_id,))
    reminders = cur.fetchall()
    cur.close()
    
    return jsonify([{
        'id': r[0],
        'text': r[1],
        'due_date': r[2].strftime('%Y-%m-%d %H:%M'),
        'status': r[3],
        'note_title': r[4],
        'note_id': r[5]
    } for r in reminders])

@app.route('/api/bookmarks')
def get_bookmarks():
    user_id = get_current_user()
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT n.note_id, n.title, n.content, b.created_at
        FROM bookmark b
        JOIN note n ON b.note_id = n.note_id
        WHERE b.user_id = %s
        ORDER BY b.created_at DESC
    """, (user_id,))
    bookmarks = cur.fetchall()
    cur.close()
    
    return jsonify([{
        'note_id': b[0],
        'title': b[1],
        'content': b[2],
        'bookmarked_at': b[3].strftime('%Y-%m-%d %H:%M')
    } for b in bookmarks])

@app.route('/api/bookmarks/<int:note_id>', methods=['POST'])
def toggle_bookmark(note_id):
    user_id = get_current_user()
    cur = mysql.connection.cursor()
    
    # Check if bookmark exists
    cur.execute("SELECT bookmark_id FROM bookmark WHERE note_id = %s AND user_id = %s", 
                (note_id, user_id))
    existing = cur.fetchone()
    
    if existing:
        cur.execute("DELETE FROM bookmark WHERE note_id = %s AND user_id = %s", 
                   (note_id, user_id))
        message = 'Bookmark removed'
        bookmarked = False
    else:
        cur.execute("INSERT INTO bookmark (note_id, user_id) VALUES (%s, %s)", 
                   (note_id, user_id))
        message = 'Bookmark added'
        bookmarked = True
    
    mysql.connection.commit()
    cur.close()
    
    return jsonify({'message': message, 'bookmarked': bookmarked})

@app.route('/api/stats')
def get_stats():
    user_id = get_current_user()
    cur = mysql.connection.cursor()
    
    # Get various statistics
    cur.execute("SELECT COUNT(*) FROM note", ())
    total_notes = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM notebook WHERE user_id = %s", (user_id,))
    total_notebooks = cur.fetchone()[0]
    
    cur.execute("""
        SELECT COUNT(*) FROM reminder 
        WHERE user_id = %s AND status = 'pending'
    """, (user_id,))
    pending_reminders = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM bookmark WHERE user_id = %s", (user_id,))
    total_bookmarks = cur.fetchone()[0]
    
    cur.close()
    
    return jsonify({
        'total_notes': total_notes,
        'total_notebooks': total_notebooks,
        'pending_reminders': pending_reminders,
        'total_bookmarks': total_bookmarks
    })

if __name__ == '__main__':
    app.run(debug=True)