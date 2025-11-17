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
- **🔍 Smart Tagging**: AI-powered tag suggestions using Google Gemini AI
  - Automatic tag generation based on note content analysis
  - Intelligent tag suggestions with confidence scores
  - Fallback keyword extraction when AI is unavailable
- **🤖 AI Chatbot Assistant**: Intelligent chatbot that can perform operations and answer questions
  - Natural language interface for all operations
  - Create, edit, delete notes through conversation
  - Manage notebooks, bookmarks, and reminders
  - Answer questions about your knowledge base
  - Execute tasks using natural language commands

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

- **Backend**: Python 3.x, Flask 2.3.3
- **Database**: MySQL 5.7+
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database Driver**: Flask-MySQLdb
- **AI**: Google Gemini API (gemini-1.5-flash/gemini-1.5-pro)
- **Environment**: python-dotenv for configuration

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
pip install -r requirements.txt
```

Or manually:
```bash
pip install flask flask-mysqldb google-generativeai python-dotenv
```

**Note:** The `requirements.txt` includes:
- Flask 2.3.3 (compatible with Flask-MySQLdb)
- Flask-MySQLdb 1.0.1
- google-generativeai 0.3.2 (for AI features)
- python-dotenv 1.0.0 (for environment variables)

### 2.1. Setup Google Gemini AI (Optional but Recommended)

The AI tag suggestion feature uses Google Gemini. To enable it:

1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Or create a `.env` file** (recommended for development):
```
GEMINI_API_KEY=your-api-key-here
FLASK_SECRET_KEY=your-secret-key-here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=admin
MYSQL_DB=pkb1
```

**Note:** 
- The app will work without the AI feature, but tag suggestions will use a fallback keyword extraction method
- The chatbot will automatically detect and use available Gemini models
- See `SETUP_ENV.md` for detailed environment variable setup instructions

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

**Option 1: Using .env file (Recommended)**
Create a `.env` file in the project root (see `env_template.txt` for template):
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=admin
MYSQL_DB=pkb1
```

**Option 2: Edit app.py directly**
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
- **🤖 AI-Powered Tag Suggestions**: Click "Auto-Suggest with AI" to automatically generate relevant tags using Google Gemini
- Manual tag suggestions with confidence scores
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

### AI Features
- `POST /api/notes/<id>/ai-suggest-tags` - Generate AI tag suggestions using Gemini
- `GET /api/ai-status` - Check if AI service is available
- `POST /api/chatbot` - Chat with AI assistant and execute operations

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

4. **AI Model Not Found Error**
   - The chatbot automatically detects and uses available Gemini models
   - If you see model errors, make sure your API key is valid
   - Try upgrading: `pip install --upgrade google-generativeai`
   - The system will automatically find a working model from your API

5. **Environment Variables Not Loading**
   - Make sure `.env` file is in the project root (same folder as `app.py`)
   - Check that `python-dotenv` is installed: `pip install python-dotenv`
   - Verify `.env` file format (no quotes around values, one per line)

## 📝 Notes

- Default user is set to user_id = 1 on first load
- Session-based user management
- All timestamps are stored in UTC
- Public notes are visible to all users (if implemented)

## 🤖 AI Features

### AI Chatbot Assistant

The application includes a powerful AI chatbot powered by Google Gemini that can:

1. **Answer Questions**: Ask questions about your knowledge base, features, or how to use the system
2. **Perform Operations**: Execute tasks using natural language:
   - "Create a note about Python programming"
   - "Show me my bookmarks"
   - "Delete the note titled 'Meeting Notes'"
   - "Create a notebook called 'Work Projects'"
   - "Bookmark note number 5"
   - "Share note 3 with user 2"
   - "Mark reminder 1 as done"
3. **Understand Context**: The chatbot has access to your notes, notebooks, categories, tags, and users
4. **Natural Language**: No need to remember commands - just talk naturally!

**How to Use:**
1. Click the "🤖 AI Assistant" button in the header
2. Type your question or command in natural language
3. The AI will understand and execute the operation
4. View the results and continue the conversation

### Google Gemini Integration

The application uses Google Gemini AI to provide intelligent tag suggestions:

1. **Automatic Tag Generation**: Analyzes note title and content to suggest relevant tags
2. **Context-Aware**: Considers existing tags in the system for better suggestions
3. **Confidence Scores**: Each suggestion includes a confidence score (0.0-1.0)
4. **Smart Fallback**: Uses keyword extraction when AI is unavailable

### How to Use AI Tag Suggestions

1. Open any note by clicking on it
2. Scroll to the "🏷️ AI Tag Suggestions" section
3. Click the "🤖 Auto-Suggest with AI" button
4. Wait for AI to analyze the content (usually 2-5 seconds)
5. Review the suggested tags with confidence scores
6. Tags are automatically added to the suggestions list

### AI Setup

Make sure to set the `GEMINI_API_KEY` environment variable for AI features to work. Without it, the app will use a fallback keyword extraction method.

## 🔮 Future Enhancements

- [x] AI-powered tag suggestions (✅ Implemented)
- [x] AI Chatbot Assistant (✅ Implemented)
- [x] Environment variable support with .env file (✅ Implemented)
- [ ] File attachments support
- [ ] Full-text search
- [ ] Export notes to PDF/Markdown
- [ ] Mobile app version
- [ ] Real-time collaboration
- [ ] Advanced analytics and insights
- [ ] AI-powered note summarization
- [ ] Content-based note recommendations

## 👥 Contributing

This is a DBMS Mini Project. For contributions:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is created for educational purposes as part of a DBMS Mini Project.

## 👨‍💻 Author
- **G Pranav Ganesh**
- **Aman Kumar Mishra**

Created as part of 5th Semester DBMS Mini Project

---

**Note**: Remember to change the secret key and database credentials before deploying to production!

