from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from ai_service import get_ai_service

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here-change-in-production')

# MySQL Configuration (from environment variables or defaults)
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'admin')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'pkb1')

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
        SELECT DISTINCT n.note_id, n.title, n.content, n.is_public, n.created_at, n.updated_at,
               c.name as category_name, nb.title as notebook_title,
               GROUP_CONCAT(DISTINCT t.name) as tags,
               (SELECT COUNT(*) FROM bookmark b WHERE b.note_id = n.note_id AND b.user_id = %s) as is_bookmarked,
               CASE 
                    WHEN n.user_id = %s THEN 'owner'
                    WHEN col.shared_with_user_id = %s THEN 'shared'
               END as note_type,
               COALESCE(col.access_level, 'owner') as access_level
        FROM note n
        LEFT JOIN collaboration col ON col.note_id = n.note_id AND col.shared_with_user_id = %s
        LEFT JOIN category c ON n.category_id = c.category_id
        LEFT JOIN notebook nb ON n.notebook_id = nb.notebook_id
        LEFT JOIN note_tag nt ON n.note_id = nt.note_id
        LEFT JOIN tag t ON nt.tag_id = t.tag_id
        WHERE n.user_id = %s OR col.shared_with_user_id = %s
        GROUP BY n.note_id, col.access_level
        ORDER BY n.updated_at DESC
    """, (user_id, user_id, user_id, user_id, user_id, user_id))
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
            'is_bookmarked': bool(note[9]),
            'note_type': note[10] if len(note) > 10 and note[10] else 'owner',
            'access_level': note[11] if len(note) > 11 else 'owner'
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
    user_id = get_current_user()
    
    cur = mysql.connection.cursor()
    
    # Check if user is owner or has write access
    cur.execute("""
        SELECT user_id FROM note WHERE note_id = %s
    """, (note_id,))
    note_owner = cur.fetchone()
    
    if not note_owner:
        cur.close()
        return jsonify({'error': 'Note not found'}), 404
    
    # If user is owner, allow update
    if note_owner[0] == user_id:
        cur.execute("""
            UPDATE note 
            SET title = %s, content = %s, is_public = %s
            WHERE note_id = %s
        """, (data['title'], data['content'], data.get('is_public', 0), note_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Note updated successfully'})
    
    # Check if user has write access via collaboration
    cur.execute("""
        SELECT access_level FROM collaboration 
        WHERE note_id = %s AND shared_with_user_id = %s
    """, (note_id, user_id))
    collab = cur.fetchone()
    
    if collab and collab[0] in ['write', 'owner']:
        cur.execute("""
            UPDATE note 
            SET title = %s, content = %s, is_public = %s
            WHERE note_id = %s
        """, (data['title'], data['content'], data.get('is_public', 0), note_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Note updated successfully'})
    
    cur.close()
    return jsonify({'error': 'You do not have permission to edit this note'}), 403

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    user_id = get_current_user()
    cur = mysql.connection.cursor()
    
    # Check if user is owner (only owners can delete)
    cur.execute("SELECT user_id FROM note WHERE note_id = %s", (note_id,))
    note_owner = cur.fetchone()
    
    if not note_owner:
        cur.close()
        return jsonify({'error': 'Note not found'}), 404
    
    if note_owner[0] != user_id:
        cur.close()
        return jsonify({'error': 'Only the owner can delete this note'}), 403
    
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

# ========== AI-POWERED AUTO TAG SUGGESTION (Gemini) ==========
@app.route('/api/notes/<int:note_id>/ai-suggest-tags', methods=['POST'])
def ai_suggest_tags(note_id):
    """Use Google Gemini AI to automatically suggest tags for a note"""
    try:
        # Get the note content
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT title, content FROM note WHERE note_id = %s
        """, (note_id,))
        note = cur.fetchone()
        
        if not note:
            cur.close()
            return jsonify({'error': 'Note not found'}), 404
        
        note_title = note[0] or ""
        note_content = note[1] or ""
        
        # Get existing tags for context
        cur.execute("SELECT name FROM tag")
        existing_tags = [row[0] for row in cur.fetchall()]
        cur.close()
        
        # Get AI service instance
        ai_service = get_ai_service()
        
        if not ai_service.is_available():
            return jsonify({
                'error': 'AI service not available. Please set GEMINI_API_KEY environment variable.',
                'available': False
            }), 503
        
        # Get AI suggestions
        suggestions = ai_service.suggest_tags_with_ai(note_title, note_content, existing_tags)
        
        if not suggestions:
            return jsonify({
                'message': 'No tag suggestions generated',
                'suggestions': [],
                'available': True
            })
        
        # Process suggestions: create tags if they don't exist and add suggestions
        cur = mysql.connection.cursor()
        results = []
        
        for tag_name, confidence in suggestions:
            # Create tag if it doesn't exist
            cur.execute("INSERT IGNORE INTO tag (name) VALUES (%s)", (tag_name,))
            cur.execute("SELECT tag_id FROM tag WHERE name = %s", (tag_name,))
            tag_row = cur.fetchone()
            
            if tag_row:
                tag_id = tag_row[0]
                
                # Check if suggestion already exists
                cur.execute("""
                    SELECT suggestion_id FROM tag_suggestion 
                    WHERE note_id = %s AND tag_id = %s
                """, (note_id, tag_id))
                
                if not cur.fetchone():
                    # Add suggestion using the stored procedure
                    cur.callproc('suggest_tag', [note_id, tag_id, confidence])
                    results.append({
                        'tag_name': tag_name,
                        'tag_id': tag_id,
                        'confidence': confidence
                    })
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'message': f'Generated {len(results)} AI tag suggestions',
            'suggestions': results,
            'available': True
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating AI suggestions: {str(e)}'}), 500

@app.route('/api/ai-status')
def ai_status():
    """Check if AI service is available"""
    ai_service = get_ai_service()
    return jsonify({
        'available': ai_service.is_available(),
        'message': 'AI service is ready' if ai_service.is_available() else 'AI service not configured. Set GEMINI_API_KEY environment variable.'
    })

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
        ORDER BY created_at DESC
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

@app.route('/api/current-user')
def get_current_user_info():
    user_id = get_current_user()
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id, name, email FROM app_user WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    
    if user:
        return jsonify({'id': user[0], 'name': user[1], 'email': user[2]})
    return jsonify({'id': 1, 'name': 'Unknown', 'email': ''})

@app.route('/api/set-user', methods=['POST'])
def set_current_user():
    data = request.json
    user_id = data.get('user_id')
    
    if user_id:
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id FROM app_user WHERE user_id = %s", (user_id,))
        if cur.fetchone():
            session['user_id'] = user_id
            cur.close()
            return jsonify({'message': 'User switched successfully', 'user_id': user_id})
        cur.close()
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'error': 'Invalid user_id'}), 400

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
    status = request.args.get('status')  # e.g., 'pending', 'done', 'skipped'
    cur = mysql.connection.cursor()
    
    if status:
        cur.execute("""
            SELECT r.reminder_id, r.reminder_text, r.due_date, r.status, n.title, n.note_id
            FROM reminder r
            JOIN note n ON r.note_id = n.note_id
            WHERE r.user_id = %s AND r.status = %s
            ORDER BY r.due_date ASC
        """, (user_id, status))
    else:
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
    
    # Get various statistics - count only user's own notes
    cur.execute("SELECT COUNT(*) FROM note WHERE user_id = %s", (user_id,))
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
    # Check AI service status on startup
    ai_service = get_ai_service()
    if ai_service.is_available():
        print("✓ AI Service (Gemini) is ready!")
    else:
        print("⚠️  AI Service not configured. Set GEMINI_API_KEY in .env file to enable AI tag suggestions.")
        print("   The app will work with fallback keyword extraction.")
    
    print(f"\n📊 Database Configuration:")
    print(f"   Host: {app.config['MYSQL_HOST']}")
    print(f"   User: {app.config['MYSQL_USER']}")
    print(f"   Database: {app.config['MYSQL_DB']}")
    print(f"\n🚀 Starting server on http://localhost:5000\n")
    
    app.run(debug=True)