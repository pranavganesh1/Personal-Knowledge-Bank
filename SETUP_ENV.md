# Environment Variables Setup Guide

## Quick Setup

1. **Create a `.env` file** in the project root directory (same folder as `app.py`)

2. **Copy the template** from `env_template.txt` or create `.env` with the following content:

```env
# Google Gemini API Key
GEMINI_API_KEY=your-api-key-here

# Flask Secret Key
FLASK_SECRET_KEY=your-secret-key-change-this-in-production

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=admin
MYSQL_DB=pkb1
```

3. **Fill in your values:**
   - **GEMINI_API_KEY**: Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **FLASK_SECRET_KEY**: Generate a random secret key (you can use: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - **MYSQL_***: Update with your MySQL credentials

## Creating the .env File

### Windows (PowerShell):
```powershell
# Copy the template
Copy-Item env_template.txt .env

# Or create manually
New-Item -Path .env -ItemType File
# Then edit it with notepad or your favorite editor
notepad .env
```

### Windows (Command Prompt):
```cmd
copy env_template.txt .env
notepad .env
```

### Linux/Mac:
```bash
cp env_template.txt .env
nano .env
```

## Example .env File

```env
GEMINI_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FLASK_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=admin
MYSQL_DB=pkb1
```

## Important Notes

- **Never commit `.env` to git!** It contains sensitive information
- The `.env` file is already in `.gitignore` (if you have one)
- If `.env` doesn't exist, the app will use default values
- You can still set environment variables manually if you prefer

## Verification

After creating `.env`, run the app:
```bash
python app.py
```

You should see:
- ✓ AI Service (Gemini) is ready! (if GEMINI_API_KEY is set)
- Database configuration displayed
- Server starting message

## Troubleshooting

**Problem**: AI service not working
- **Solution**: Check that `GEMINI_API_KEY` is set correctly in `.env`
- Make sure there are no quotes around the value in `.env`

**Problem**: Database connection error
- **Solution**: Verify MySQL credentials in `.env` match your MySQL setup
- Make sure MySQL server is running

**Problem**: `.env` file not being read
- **Solution**: Make sure `.env` is in the same directory as `app.py`
- Check that `python-dotenv` is installed: `pip install python-dotenv`

