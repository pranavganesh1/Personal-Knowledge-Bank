"""
AI Service for Automatic Tag Suggestions using Google Gemini
Analyzes note content and suggests relevant tags with confidence scores
"""

import os
import re
from typing import List, Dict, Tuple
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. AI features will be disabled.")


class AITagSuggestionService:
    """Service for generating AI-powered tag suggestions using Google Gemini"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the AI service with Gemini API
        
        Args:
            api_key: Google Gemini API key. If None, will try to get from environment variable GEMINI_API_KEY
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not set. AI features will be disabled.")
            self.model = None
            return
        
        if not GEMINI_AVAILABLE:
            self.model = None
            return
        
        try:
            genai.configure(api_key=self.api_key)
            # Use gemini-pro model for text analysis
            self.model = genai.GenerativeModel('gemini-pro')
            print("✓ Gemini AI initialized successfully")
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.model is not None and GEMINI_AVAILABLE
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text using simple NLP techniques
        Falls back to keyword extraction if AI is not available
        """
        if not text:
            return []
        
        # Simple keyword extraction: remove common stop words and extract meaningful words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        # Extract words (alphanumeric, at least 3 characters)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out stop words and get unique words
        keywords = [w for w in words if w not in stop_words]
        
        # Return top keywords (most frequent)
        from collections import Counter
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(10)]
    
    def suggest_tags_with_ai(self, note_title: str, note_content: str, existing_tags: List[str] = None) -> List[Tuple[str, float]]:
        """
        Use Gemini AI to analyze note content and suggest relevant tags
        
        Args:
            note_title: Title of the note
            note_content: Content of the note
            existing_tags: List of existing tags in the system (optional, for context)
        
        Returns:
            List of tuples (tag_name, confidence_score) sorted by confidence
        """
        if not self.is_available():
            # Fallback to keyword extraction
            return self._fallback_suggestions(note_title, note_content, existing_tags)
        
        try:
            # Prepare the prompt for Gemini
            existing_tags_str = ""
            if existing_tags:
                existing_tags_str = f"\n\nExisting tags in the system: {', '.join(existing_tags[:20])}"
            
            prompt = f"""Analyze the following note and suggest 3-5 relevant tags that best describe its content, topic, and purpose.

Note Title: {note_title}

Note Content:
{note_content[:2000]}{existing_tags_str}

Instructions:
1. Suggest 3-5 tags that are most relevant to this note
2. Tags should be concise (1-2 words), lowercase, and descriptive
3. Consider the main topic, category, purpose, and key concepts
4. If the note is about a todo/task, suggest "todo" tag
5. If the note is about learning/study, suggest "study" or "learning"
6. Return ONLY a JSON array of objects, each with "tag" and "confidence" (0.0-1.0) fields
7. Format: [{{"tag": "tag_name", "confidence": 0.85}}, ...]

Example response:
[{{"tag": "programming", "confidence": 0.9}}, {{"tag": "python", "confidence": 0.8}}, {{"tag": "tutorial", "confidence": 0.75}}]

Return only the JSON array, no other text:"""

            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean the response (remove markdown code blocks if present)
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            response_text = response_text.strip()
            
            # Parse JSON response
            import json
            suggestions = json.loads(response_text)
            
            # Validate and format results
            results = []
            for item in suggestions:
                if isinstance(item, dict) and 'tag' in item and 'confidence' in item:
                    tag_name = item['tag'].lower().strip()
                    confidence = float(item['confidence'])
                    # Clamp confidence between 0 and 1
                    confidence = max(0.0, min(1.0, confidence))
                    if tag_name:
                        results.append((tag_name, confidence))
            
            # Sort by confidence (descending)
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results[:5]  # Return top 5 suggestions
            
        except Exception as e:
            print(f"Error in AI tag suggestion: {e}")
            # Fallback to keyword extraction
            return self._fallback_suggestions(note_title, note_content, existing_tags)
    
    def _fallback_suggestions(self, note_title: str, note_content: str, existing_tags: List[str] = None) -> List[Tuple[str, float]]:
        """
        Fallback method when AI is not available
        Uses keyword extraction and simple matching
        """
        text = f"{note_title} {note_content}".lower()
        keywords = self.extract_keywords(text)
        
        # Match keywords with existing tags if provided
        suggestions = []
        if existing_tags:
            existing_tags_lower = [t.lower() for t in existing_tags]
            for keyword in keywords[:5]:
                # Check for exact or partial matches
                for tag in existing_tags_lower:
                    if keyword in tag or tag in keyword:
                        confidence = 0.7 if keyword == tag else 0.5
                        suggestions.append((tag, confidence))
                        break
                else:
                    # New tag suggestion
                    suggestions.append((keyword, 0.6))
        else:
            # Just suggest keywords as tags
            suggestions = [(kw, 0.6) for kw in keywords[:5]]
        
        # Remove duplicates and sort
        seen = set()
        unique_suggestions = []
        for tag, conf in suggestions:
            if tag not in seen:
                seen.add(tag)
                unique_suggestions.append((tag, conf))
        
        return unique_suggestions[:5]
    
    def analyze_note_summary(self, note_content: str) -> str:
        """
        Generate a brief summary of the note using AI
        """
        if not self.is_available() or not note_content:
            return ""
        
        try:
            prompt = f"""Provide a brief 1-2 sentence summary of the following note content:

{note_content[:1500]}

Summary:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return ""


# Global instance
_ai_service = None

def get_ai_service(api_key: str = None) -> AITagSuggestionService:
    """Get or create the global AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AITagSuggestionService(api_key)
    return _ai_service

