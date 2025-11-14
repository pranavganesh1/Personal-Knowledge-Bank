"""
AI Chatbot Service for Knowledge Base Management
Uses Google Gemini to understand natural language and execute operations
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class KnowledgeBaseChatbot:
    """Chatbot that can answer questions and perform operations on the Knowledge Base"""
    
    def __init__(self, api_key: str = None):
        """Initialize the chatbot with Gemini API"""
        self.api_key = api_key
        self.model = None
        self.conversation_history = []
        
        if api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=api_key)
                # Try different model names - Google has changed model names over time
                model_names = [
                    'gemini-1.5-flash',
                    'gemini-1.5-pro',
                    'gemini-pro',
                    'models/gemini-1.5-flash',
                    'models/gemini-1.5-pro',
                    'models/gemini-pro'
                ]
                
                self.model = None
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        print(f"✓ Chatbot initialized with model: {model_name}")
                        break
                    except Exception as e:
                        continue
                
                if not self.model:
                    # Last resort: list available models
                    try:
                        models = genai.list_models()
                        for model in models:
                            if 'generateContent' in model.supported_generation_methods:
                                model_name = model.name
                                # Remove 'models/' prefix if present
                                if model_name.startswith('models/'):
                                    model_name = model_name[7:]
                                
                                try:
                                    self.model = genai.GenerativeModel(model_name)
                                    print(f"✓ Chatbot initialized with available model: {model_name}")
                                    break
                                except:
                                    continue
                    except Exception as e:
                        print(f"Error listing models: {e}")
                        
            except Exception as e:
                print(f"Error initializing chatbot: {e}")
    
    def is_available(self) -> bool:
        """Check if chatbot is available"""
        return self.model is not None and GEMINI_AVAILABLE
    
    def _try_find_working_model(self) -> bool:
        """Try to find a working model by listing available models"""
        if not self.api_key or not GEMINI_AVAILABLE:
            return False
        
        try:
            import google.generativeai as genai
            models = genai.list_models()
            
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    model_name = model.name
                    # Remove 'models/' prefix if present
                    if model_name.startswith('models/'):
                        model_name = model_name[7:]
                    
                    try:
                        # Try to create and test the model
                        test_model = genai.GenerativeModel(model_name)
                        # Quick test call
                        test_model.generate_content("Hi")
                        # If successful, use this model
                        self.model = test_model
                        print(f"✓ Switched to working model: {model_name}")
                        return True
                    except:
                        continue
        except Exception as e:
            print(f"Error finding working model: {e}")
        
        return False
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the chatbot's capabilities"""
        return """You are an AI assistant for a Personal Knowledge Base Management System. You can help users manage their notes, notebooks, bookmarks, reminders, and more.

AVAILABLE OPERATIONS:

1. NOTES:
   - create_note(title, content, category_id=None, notebook_id=None, tags=[], is_public=False)
   - get_notes() - List all notes
   - get_note(note_id) - Get specific note
   - update_note(note_id, title=None, content=None, is_public=None)
   - delete_note(note_id)
   - search_notes(query) - Search notes by title/content

2. NOTEBOOKS:
   - create_notebook(title, description=None)
   - get_notebooks() - List all notebooks
   - get_notebook(notebook_id)

3. BOOKMARKS:
   - bookmark_note(note_id)
   - unbookmark_note(note_id)
   - get_bookmarks() - List bookmarked notes

4. REMINDERS:
   - get_reminders(status='pending') - Get reminders (status: pending, done, skipped)
   - mark_reminder_done(reminder_id)

5. TAGS & CATEGORIES:
   - get_tags() - List all tags
   - get_categories() - List all categories
   - add_tags_to_note(note_id, tags) - Add tags to a note

6. COLLABORATION:
   - share_note(note_id, user_id, access_level='read') - Share note (access_level: read, write, owner)
   - get_collaborators(note_id) - Get note collaborators

7. STATISTICS:
   - get_stats() - Get user statistics

8. USERS:
   - get_users() - List all users
   - get_current_user() - Get current user info

When a user asks you to perform an operation, respond with a JSON object in this format:
{
    "action": "operation_name",
    "parameters": {...},
    "message": "Friendly message explaining what you're doing"
}

For questions or information requests, respond with:
{
    "action": "answer",
    "message": "Your helpful answer"
}

If you need to ask for clarification, use:
{
    "action": "clarify",
    "message": "What you need to know"
}

IMPORTANT:
- Always be helpful and friendly
- When creating notes, extract title and content from user's request
- For tags, extract relevant keywords from the content
- Use natural language in your messages
- If a note_id is needed but not provided, ask the user
"""

    def process_message(self, user_message: str, context: Dict = None) -> Dict:
        """
        Process a user message and determine the action to take
        
        Args:
            user_message: The user's message
            context: Additional context (current user, available data, etc.)
        
        Returns:
            Dict with action, parameters, and message
        """
        if not self.is_available():
            return {
                "action": "answer",
                "message": "I'm sorry, the AI chatbot is not available. Please set GEMINI_API_KEY in your .env file."
            }
        
        try:
            # Build context information
            context_info = ""
            if context:
                if 'notes' in context:
                    context_info += f"\n\nAvailable Notes (first 5): {json.dumps(context['notes'][:5], indent=2)}"
                if 'notebooks' in context:
                    context_info += f"\n\nAvailable Notebooks: {json.dumps(context['notebooks'], indent=2)}"
                if 'categories' in context:
                    context_info += f"\n\nAvailable Categories: {json.dumps(context['categories'], indent=2)}"
                if 'tags' in context:
                    context_info += f"\n\nAvailable Tags: {json.dumps(context['tags'], indent=2)}"
                if 'users' in context:
                    context_info += f"\n\nAvailable Users: {json.dumps(context['users'], indent=2)}"
                if 'current_user' in context:
                    context_info += f"\n\nCurrent User: {json.dumps(context['current_user'], indent=2)}"
            
            # Build the prompt
            prompt = f"""{self.get_system_prompt()}

{context_info}

User Message: "{user_message}"

Analyze the user's request and respond with a JSON object. If the user wants to perform an operation, provide the action and parameters. If it's a question, provide an answer.

Response (JSON only):"""

            # Get response from Gemini - with retry logic if model fails
            try:
                response = self.model.generate_content(prompt)
                response_text = response.text.strip()
            except Exception as model_error:
                # If model call fails, try to find a working model
                if "404" in str(model_error) or "not found" in str(model_error).lower():
                    print(f"Model failed, trying to find working model...")
                    if self._try_find_working_model():
                        # Retry with new model
                        response = self.model.generate_content(prompt)
                        response_text = response.text.strip()
                    else:
                        raise model_error
                else:
                    raise model_error
            
            # Clean the response (remove markdown code blocks if present)
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            response_text = response_text.strip()
            
            # Try to parse JSON response
            try:
                result = json.loads(response_text)
                
                # Validate the response structure
                if 'action' not in result:
                    result = {"action": "answer", "message": response_text}
                
                return result
                
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as a direct answer
                return {
                    "action": "answer",
                    "message": response_text
                }
                
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                "action": "answer",
                "message": f"I encountered an error: {str(e)}. Please try rephrasing your request."
            }
    
    def extract_note_info(self, message: str) -> Dict:
        """
        Extract note information from a natural language message
        This is a fallback if the AI doesn't provide structured data
        """
        # Simple extraction patterns
        title_match = re.search(r'title[:\s]+["\']?([^"\']+)["\']?', message, re.IGNORECASE)
        content_match = re.search(r'content[:\s]+["\']?([^"\']+)["\']?', message, re.IGNORECASE)
        
        # Try to extract title and content from common patterns
        if not title_match:
            # Look for "create note about X" or "note: X"
            title_match = re.search(r'(?:note|about|titled?)[:\s]+["\']?([^"\']{1,100})["\']?', message, re.IGNORECASE)
        
        return {
            "title": title_match.group(1) if title_match else "Untitled Note",
            "content": content_match.group(1) if content_match else message
        }


# Global chatbot instance
_chatbot = None

def get_chatbot(api_key: str = None) -> KnowledgeBaseChatbot:
    """Get or create the global chatbot instance"""
    global _chatbot
    if _chatbot is None:
        _chatbot = KnowledgeBaseChatbot(api_key)
    return _chatbot

