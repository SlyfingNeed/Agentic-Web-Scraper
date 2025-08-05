import os
import asyncio
from typing import Dict, List, Any, Optional
import google.generativeai as genai
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingAgent:
    """
    AI agent that uses Google Gemini to:
    1. Interpret natural language queries and determine scraping strategy
    2. Extract structured data from HTML content
    """
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Predefined website mappings for common queries
        self.website_mappings = {
            "cnn": "https://www.cnn.com",
            "bbc": "https://www.bbc.com/news",
            "reuters": "https://www.reuters.com",
            "techcrunch": "https://techcrunch.com",
            "wired": "https://www.wired.com",
            "ars technica": "https://arstechnica.com",
            "the verge": "https://www.theverge.com",
            "reddit": "https://www.reddit.com",
            "hacker news": "https://news.ycombinator.com",
            "medium": "https://medium.com"
        }
    
    def is_ready(self) -> bool:
        """Check if the agent is properly initialized"""
        return bool(self.gemini_api_key and self.model)
    
    async def interpret_query(self, query: str) -> Dict[str, Any]:
        """
        Use AI to interpret the query and determine:
        - Target website URL
        - What elements to scrape
        - Scraping strategy
        """
        try:
            # First, try to extract website from query
            website = self._extract_website_from_query(query.lower())
            
            # Create prompt for query interpretation
            system_prompt = """You are an expert web scraping strategist. Given a natural language query, determine:
1. The target website URL (if not already provided)
2. What type of content to scrape (articles, products, etc.)
3. The CSS selectors or element types to target
4. Any specific data fields to extract

Respond with a JSON object containing:
{
    "url": "target_website_url",
    "target_elements": ["article", "div.article", "h1", "h2", "a"],
    "data_fields": ["title", "link", "summary", "date"],
    "strategy": "description of scraping approach"
}"""

            user_prompt = f"""
Query: {query}

Current website mapping: {website if website else "None detected"}

Please provide a scraping strategy for this query.
"""

            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Use Gemini to generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt
            )
            
            # Parse the response
            try:
                # Extract JSON from response
                response_text = response.text
                # Find JSON in the response (handle cases where there's extra text)
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    strategy = json.loads(json_str)
                else:
                    raise json.JSONDecodeError("No JSON found in response", response_text, 0)
                
                # If no URL was detected in the query, use the mapped website
                if not strategy.get("url") and website:
                    strategy["url"] = website
                
                # Add default target elements if not specified
                if not strategy.get("target_elements"):
                    strategy["target_elements"] = ["article", "div.article", "h1", "h2", "a"]
                
                # Add default data fields if not specified
                if not strategy.get("data_fields"):
                    strategy["data_fields"] = ["title", "link", "summary", "date"]
                
                logger.info(f"Scraping strategy: {strategy}")
                return strategy
                
            except json.JSONDecodeError:
                # Fallback strategy if JSON parsing fails
                logger.warning("Failed to parse AI response as JSON, using fallback strategy")
                return {
                    "url": website or "https://www.google.com",
                    "target_elements": ["article", "div.article", "h1", "h2", "a"],
                    "data_fields": ["title", "link", "summary", "date"],
                    "strategy": "Fallback strategy due to parsing error"
                }
                
        except Exception as e:
            logger.error(f"Error interpreting query: {e}")
            raise Exception(f"Failed to interpret query: {str(e)}")
    
    async def extract_data(self, html_content: str, target_elements: List[str], original_query: str) -> List[Dict[str, Any]]:
        """
        Use AI to extract structured data from HTML content based on the original query
        """
        try:
            # Truncate HTML content to avoid token limits (keep first 8000 chars)
            truncated_html = html_content[:8000] + "..." if len(html_content) > 8000 else html_content
            
            system_prompt = """You are an expert at extracting structured data from HTML content. 
Given HTML content and a list of target elements, extract relevant information and return it as a JSON array.

For each item found, create an object with these fields:
- title: The title or headline
- link: The URL link (if available)
- summary: A brief summary or description
- date: Publication date (if available)
- source: The source website
- category: Content category (if identifiable)

Return ONLY valid JSON array, no additional text."""

            user_prompt = f"""
Original Query: {original_query}

Target Elements: {', '.join(target_elements)}

HTML Content:
{truncated_html}

Extract relevant data and return as JSON array.
"""

            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Use Gemini to generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt
            )
            
            # Parse the response
            try:
                # Extract JSON from response
                response_text = response.text
                # Find JSON in the response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    extracted_data = json.loads(json_str)
                else:
                    # Try to find object and wrap in array
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = response_text[start_idx:end_idx]
                        extracted_data = [json.loads(json_str)]
                    else:
                        raise json.JSONDecodeError("No JSON found in response", response_text, 0)
                
                # Ensure it's a list
                if not isinstance(extracted_data, list):
                    extracted_data = [extracted_data]
                
                # Clean and validate the data
                cleaned_data = []
                for item in extracted_data:
                    if isinstance(item, dict):
                        cleaned_item = {
                            "title": item.get("title", ""),
                            "link": item.get("link", ""),
                            "summary": item.get("summary", ""),
                            "date": item.get("date", ""),
                            "source": item.get("source", ""),
                            "category": item.get("category", "")
                        }
                        cleaned_data.append(cleaned_item)
                
                logger.info(f"Extracted {len(cleaned_data)} items")
                return cleaned_data
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse extracted data as JSON")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            return []
    
    def _extract_website_from_query(self, query: str) -> Optional[str]:
        """
        Extract website URL from query using keyword matching
        """
        query_lower = query.lower()
        
        for keyword, url in self.website_mappings.items():
            if keyword in query_lower:
                return url
        
        # Check for specific patterns
        if "bitcoin" in query_lower and "cnn" in query_lower:
            return "https://www.cnn.com"
        elif "tech" in query_lower and "news" in query_lower:
            return "https://techcrunch.com"
        elif "reddit" in query_lower:
            return "https://www.reddit.com"
        
        return None 