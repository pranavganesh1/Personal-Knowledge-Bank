# 📚 Knowledge Base Pro

A comprehensive Personal Knowledge Base Management System built with Flask and MySQL. This application allows users to create, organize, and manage their notes, notebooks, bookmarks, and reminders with advanced features like collaboration, version history, and automated reminders.

## ✨ Features

### Core Features
- **📝 Note Management**: Create, edit, and delete notes with rich content
- **📒 Notebook Organization**: Organize notes into custom notebooks
- **⭐ Bookmarks**: Bookmark important notes for quick access
- **⏰ Reminders**: Set reminders for notes with due dates
- **🏷️ Tags & Categories**: Categorize and tag notes for better organization
- **👥 Collaboration**: Share notes with other users with read/write permissions
- **📜 Version History**: Automatic version tracking when notes are edited
- **🔍 Smart Tagging**: AI-powered tag suggestions for notes

### Advanced Features
- **User Management**: Multi-user support with user switching
- **Access Control**: Fine-grained permissions (read/write/owner)
- **Automated Triggers**: 
  - Auto-create reminders when "todo" tag is added
  - Version history on note updates
  - Notebook timestamp updates
- **Stored Procedures**: 
  - Share notes with users
  - Suggest tags with confidence scores
  - Mark reminders as done

## 🛠️ Tech Stack

- **Backend**: Python 3.x, Flask
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database Driver**: Flask-MySQLdb

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.7 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd "Mini Project"
```

### 2. Install Python Dependencies
```bash
pip install flask flask-mysqldb
```

### 3. Database Setup

1. Start your MySQL server
2. Open MySQL command line or MySQL Workbench
3. Run the database schema file (create the SQL file from your schema or run the DDL statements)

The database schema includes:
- `app_user` - User accounts
- `notebook` - User notebooks
- `category` - Note categories
- `category_hierarchy` - Category relationships
- `note` - Main notes table
- `note_history` - Version history
- `tag` - Available tags
- `note_tag` - Note-tag relationships
- `attachment` - File attachments
- `collaboration` - Shared notes
- `comment` - Note comments
- `reminder` - User reminders
- `tag_suggestion` - AI tag suggestions
- `bookmark` - User bookmarks

### 4. Configure Database Connection

Edit `app.py` and update the MySQL configuration:

```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Your MySQL username
app.config['MYSQL_PASSWORD'] = 'admin'  # Your MySQL password
app.config['MYSQL_DB'] = 'pkb1'  # Your database name
```

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📖 Usage Guide

### Getting Started

1. **Access the Application**: Open your browser and navigate to `http://localhost:5000`

2. **Switch Users**: Use the dropdown in the top-right corner to switch between users

3. **Create a Note**: 
   - Click the "✍️ New Note" button
   - Fill in the title, content, category, notebook, and tags
   - Check "Make this note public" if you want it visible to all users
   - Click "Save Note"

4. **View Notes**: All your notes are displayed in the "All Notes" tab

5. **Edit/Delete Notes**: 
   - Click the edit (✏️) or delete (🗑️) icons on your notes
   - Only note owners can delete notes
   - Users with write access can edit shared notes

6. **Bookmark Notes**: Click the star (⭐) icon to bookmark important notes

7. **Share Notes**: 
   - Open a note's details
   - Go to the "Collaborators" section
   - Click "+ Share Note"
   - Select a user and access level (read/write/owner)
   - The shared note will appear in the recipient's notes list

8. **Set Reminders**: 
   - Add a "todo" tag to a note (automatically creates a reminder)
   - Or manually create reminders in the Reminders tab

### Features Overview

#### 📊 Dashboard
- View statistics: Total Notes, Notebooks, Pending Reminders, Bookmarks
- Click on stat cards to filter and view specific content

#### 📝 Notes
- Create and manage notes with categories and tags
- View version history for edited notes
- See AI tag suggestions
- Manage collaborators

#### 📒 Notebooks
- Organize notes into notebooks
- View all notebooks in the Notebooks tab

#### ⭐ Bookmarks
- Quick access to your bookmarked notes
- Bookmark any note with a single click

#### ⏰ Reminders
- View pending reminders
- Mark reminders as done
- Auto-created when "todo" tag is added

## 🔌 API Endpoints

### Notes
- `GET /api/notes` - Get all notes for current user
- `GET /api/notes/<id>` - Get specific note details
- `POST /api/notes` - Create new note
- `PUT /api/notes/<id>` - Update note (requires ownership or write access)
- `DELETE /api/notes/<id>` - Delete note (owner only)

### Collaboration
- `POST /api/notes/<id>/share` - Share note with user
- `GET /api/notes/<id>/collaborators` - Get note collaborators

### Bookmarks
- `GET /api/bookmarks` - Get user's bookmarks
- `POST /api/bookmarks/<id>` - Toggle bookmark

### Reminders
- `GET /api/reminders?status=pending` - Get reminders (filter by status)
- `POST /api/reminders/<id>/done` - Mark reminder as done

### Statistics
- `GET /api/stats` - Get user statistics

### User Management
- `GET /api/users` - Get all users
- `GET /api/current-user` - Get current user
- `POST /api/set-user` - Switch current user

## 🗄️ Database Features

### Triggers

1. **`trg_note_version`**: Automatically creates version history when a note is updated
2. **`trg_notebook_updated`**: Updates notebook timestamp when notes are modified
3. **`trg_auto_todo_reminder`**: Automatically creates a reminder when "todo" tag is added to a note

### Stored Procedures

1. **`suggest_tag(note_id, tag_id, confidence)`**: Suggest a tag for a note with confidence score
2. **`share_note(note_id, user_id, access_level)`**: Share a note with a user (read/write/owner)
3. **`mark_reminder_done(reminder_id)`**: Mark a reminder as completed

## 🔐 Access Control

- **Owner**: Full control (create, read, update, delete)
- **Write Access**: Can read and edit shared notes, cannot delete
- **Read Access**: Can only view shared notes, cannot edit or delete

## 📸 Features Showcase

### User Interface
- Modern dark theme with purple gradient accents
- Responsive design for all screen sizes
- Intuitive navigation with tabs and stat cards
- Real-time updates and smooth animations

### Collaboration
- Share notes with specific users
- Set access levels (read/write)
- View shared notes with clear indicators
- Edit shared notes with write permission

### Automation
- Auto-reminders for todo items
- Version history tracking
- Smart tag suggestions

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify MySQL server is running
   - Check database credentials in `app.py`
   - Ensure database `pkb1` exists

2. **Module Not Found Error**
   - Install dependencies: `pip install flask flask-mysqldb`
   - Verify Python version: `python --version`

3. **Port Already in Use**
   - Change port in `app.py`: `app.run(debug=True, port=5001)`

## 📝 Notes

- Default user is set to user_id = 1 on first load
- Session-based user management
- All timestamps are stored in UTC
- Public notes are visible to all users (if implemented)

## 🔮 Future Enhancements

- [ ] File attachments support
- [ ] Full-text search
- [ ] Export notes to PDF/Markdown
- [ ] Mobile app version
- [ ] Real-time collaboration
- [ ] Advanced analytics and insights

## 👥 Contributing

This is a DBMS Mini Project. For contributions:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is created for educational purposes as part of a DBMS Mini Project.

## 👨‍💻 Author
G Pranav Ganesh
Aman Kumar Mishra

Created as part of 5th Semester DBMS Mini Project

---

**Note**: Remember to change the secret key and database credentials before deploying to production!

