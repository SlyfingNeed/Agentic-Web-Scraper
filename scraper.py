from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import re
import logging
from urllib.parse import urljoin, urlparse
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HTMLScraper:
    """
    HTML parsing and data extraction using BeautifulSoup.
    Provides methods to extract structured data from HTML content.
    """
    
    def __init__(self):
        # Common selectors for different types of content
        self.selectors = {
            "articles": [
                "article",
                ".article",
                ".post",
                ".story",
                ".content-item",
                "[class*='article']",
                "[class*='post']",
                "[class*='story']"
            ],
            "titles": [
                "h1",
                "h2",
                "h3",
                ".title",
                ".headline",
                "[class*='title']",
                "[class*='headline']"
            ],
            "links": [
                "a[href]",
                ".link",
                "[class*='link']"
            ],
            "summaries": [
                ".summary",
                ".excerpt",
                ".description",
                ".content",
                "p",
                "[class*='summary']",
                "[class*='excerpt']"
            ],
            "dates": [
                ".date",
                ".time",
                ".published",
                "[datetime]",
                "[class*='date']",
                "[class*='time']"
            ]
        }
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup
        
        Args:
            html_content: Raw HTML string
        
        Returns:
            BeautifulSoup object
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            raise Exception(f"HTML parsing failed: {str(e)}")
    
    def extract_articles(self, html_content: str, base_url: str = "") -> List[Dict[str, Any]]:
        """
        Extract article-like content from HTML
        
        Args:
            html_content: Raw HTML string
            base_url: Base URL for resolving relative links
        
        Returns:
            List of article dictionaries
        """
        try:
            soup = self.parse_html(html_content)
            articles = []
            
            # Find potential article containers
            article_elements = []
            for selector in self.selectors["articles"]:
                elements = soup.select(selector)
                article_elements.extend(elements)
            
            # If no specific article containers found, look for content areas
            if not article_elements:
                article_elements = soup.find_all(['div', 'section'], class_=re.compile(r'article|post|story|content'))
            
            for element in article_elements:
                article_data = self._extract_article_data(element, base_url)
                if article_data and self._is_valid_article(article_data):
                    articles.append(article_data)
            
            logger.info(f"Extracted {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error extracting articles: {e}")
            return []
    
    def extract_links(self, html_content: str, base_url: str = "") -> List[Dict[str, str]]:
        """
        Extract all links from HTML content
        
        Args:
            html_content: Raw HTML string
            base_url: Base URL for resolving relative links
        
        Returns:
            List of link dictionaries
        """
        try:
            soup = self.parse_html(html_content)
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if href and text:
                    # Resolve relative URLs
                    full_url = urljoin(base_url, href)
                    
                    links.append({
                        "text": text,
                        "url": full_url,
                        "title": link.get('title', '')
                    })
            
            logger.info(f"Extracted {len(links)} links")
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []
    
    def extract_headlines(self, html_content: str) -> List[str]:
        """
        Extract headlines from HTML content
        
        Args:
            html_content: Raw HTML string
        
        Returns:
            List of headline strings
        """
        try:
            soup = self.parse_html(html_content)
            headlines = []
            
            # Find all heading elements
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                text = heading.get_text(strip=True)
                if text and len(text) > 10:  # Filter out short headings
                    headlines.append(text)
            
            logger.info(f"Extracted {len(headlines)} headlines")
            return headlines
            
        except Exception as e:
            logger.error(f"Error extracting headlines: {e}")
            return []
    
    def extract_metadata(self, html_content: str) -> Dict[str, Any]:
        """
        Extract metadata from HTML (title, description, keywords, etc.)
        
        Args:
            html_content: Raw HTML string
        
        Returns:
            Dictionary of metadata
        """
        try:
            soup = self.parse_html(html_content)
            metadata = {}
            
            # Title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text(strip=True)
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                metadata['description'] = meta_desc.get('content', '')
            
            # Meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                metadata['keywords'] = meta_keywords.get('content', '')
            
            # Open Graph tags
            og_tags = {}
            for tag in soup.find_all('meta', property=re.compile(r'^og:')):
                property_name = tag.get('property', '').replace('og:', '')
                og_tags[property_name] = tag.get('content', '')
            
            if og_tags:
                metadata['open_graph'] = og_tags
            
            # Twitter Card tags
            twitter_tags = {}
            for tag in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
                name = tag.get('name', '').replace('twitter:', '')
                twitter_tags[name] = tag.get('content', '')
            
            if twitter_tags:
                metadata['twitter'] = twitter_tags
            
            logger.info(f"Extracted metadata: {list(metadata.keys())}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}
    
    def _extract_article_data(self, element, base_url: str) -> Optional[Dict[str, Any]]:
        """
        Extract data from a single article element
        
        Args:
            element: BeautifulSoup element
            base_url: Base URL for resolving relative links
        
        Returns:
            Article data dictionary or None
        """
        try:
            article_data = {}
            
            # Extract title
            title = self._extract_title(element)
            if title:
                article_data['title'] = title
            
            # Extract link
            link = self._extract_link(element, base_url)
            if link:
                article_data['link'] = link
            
            # Extract summary
            summary = self._extract_summary(element)
            if summary:
                article_data['summary'] = summary
            
            # Extract date
            date = self._extract_date(element)
            if date:
                article_data['date'] = date
            
            # Extract image
            image = self._extract_image(element, base_url)
            if image:
                article_data['image'] = image
            
            return article_data if article_data else None
            
        except Exception as e:
            logger.warning(f"Error extracting article data: {e}")
            return None
    
    def _extract_title(self, element) -> Optional[str]:
        """Extract title from element"""
        # Look for heading elements first
        for heading in element.find_all(['h1', 'h2', 'h3', 'h4']):
            text = heading.get_text(strip=True)
            if text and len(text) > 5:
                return text
        
        # Look for title classes
        for selector in self.selectors["titles"]:
            title_elem = element.select_one(selector)
            if title_elem:
                text = title_elem.get_text(strip=True)
                if text and len(text) > 5:
                    return text
        
        return None
    
    def _extract_link(self, element, base_url: str) -> Optional[str]:
        """Extract link from element"""
        # Look for links within the element
        link_elem = element.find('a', href=True)
        if link_elem:
            href = link_elem.get('href', '')
            if href:
                return urljoin(base_url, href)
        
        # Check if the element itself is a link
        if element.name == 'a' and element.get('href'):
            href = element.get('href', '')
            if href:
                return urljoin(base_url, href)
        
        return None
    
    def _extract_summary(self, element) -> Optional[str]:
        """Extract summary from element"""
        # Look for summary classes
        for selector in self.selectors["summaries"]:
            summary_elem = element.select_one(selector)
            if summary_elem:
                text = summary_elem.get_text(strip=True)
                if text and len(text) > 20:
                    return text[:300]  # Limit summary length
        
        # Look for paragraphs
        paragraphs = element.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 50:
                return text[:300]
        
        return None
    
    def _extract_date(self, element) -> Optional[str]:
        """Extract date from element"""
        # Look for date classes
        for selector in self.selectors["dates"]:
            date_elem = element.select_one(selector)
            if date_elem:
                # Check for datetime attribute first
                datetime_attr = date_elem.get('datetime')
                if datetime_attr:
                    return datetime_attr
                
                # Otherwise use text content
                text = date_elem.get_text(strip=True)
                if text:
                    return text
        
        return None
    
    def _extract_image(self, element, base_url: str) -> Optional[str]:
        """Extract image from element"""
        # Look for images
        img_elem = element.find('img', src=True)
        if img_elem:
            src = img_elem.get('src', '')
            if src:
                return urljoin(base_url, src)
        
        return None
    
    def _is_valid_article(self, article_data: Dict[str, Any]) -> bool:
        """Check if article data is valid and complete enough"""
        # Must have at least a title or link
        has_title = bool(article_data.get('title'))
        has_link = bool(article_data.get('link'))
        
        return has_title or has_link
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Raw text string
        
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)]', '', text)
        
        return text.strip()
    
    def extract_structured_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract structured data (JSON-LD, Microdata) from HTML
        
        Args:
            html_content: Raw HTML string
        
        Returns:
            List of structured data objects
        """
        try:
            soup = self.parse_html(html_content)
            structured_data = []
            
            # Extract JSON-LD scripts
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        structured_data.extend(data)
                    else:
                        structured_data.append(data)
                except json.JSONDecodeError:
                    continue
            
            # Extract Microdata
            for item in soup.find_all(attrs={'itemtype': True}):
                microdata = self._extract_microdata(item)
                if microdata:
                    structured_data.append(microdata)
            
            logger.info(f"Extracted {len(structured_data)} structured data items")
            return structured_data
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return []
    
    def _extract_microdata(self, element) -> Optional[Dict[str, Any]]:
        """Extract microdata from an element"""
        try:
            itemtype = element.get('itemtype', '')
            if not itemtype:
                return None
            
            microdata = {
                'type': itemtype,
                'properties': {}
            }
            
            # Extract properties
            for prop_elem in element.find_all(attrs={'itemprop': True}):
                prop_name = prop_elem.get('itemprop')
                prop_value = prop_elem.get('content') or prop_elem.get_text(strip=True)
                
                if prop_name and prop_value:
                    microdata['properties'][prop_name] = prop_value
            
            return microdata if microdata['properties'] else None
            
        except Exception as e:
            logger.warning(f"Error extracting microdata: {e}")
            return None 