import asyncio
from playwright.async_api import async_playwright, Browser, Page
from typing import Optional
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserManager:
    """
    Manages Playwright browser instances for web scraping.
    Handles page loading, JavaScript rendering, and browser lifecycle.
    """
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the browser instance"""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with appropriate settings for scraping
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # Run in headless mode for server deployment
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                ]
            )
            
            # Create a new page
            self.page = await self.browser.new_page()
            
            # Set viewport
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Set default timeout
            self.page.set_default_timeout(30000)  # 30 seconds
            
            # Add request interception to block unnecessary resources
            await self.page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,otf}", self._block_resource)
            
            self.is_initialized = True
            logger.info("Browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise Exception(f"Browser initialization failed: {str(e)}")
    
    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            self.is_initialized = False
            logger.info("Browser cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")
    
    async def is_ready(self) -> bool:
        """Check if browser is ready for use"""
        return self.is_initialized and self.browser and self.page
    
    async def get_page_content(self, url: str, wait_time: int = 3) -> Optional[str]:
        """
        Navigate to URL, wait for page to load, and return HTML content
        
        Args:
            url: The URL to navigate to
            wait_time: Time to wait after page load for dynamic content (seconds)
        
        Returns:
            HTML content as string or None if failed
        """
        if not self.is_ready():
            logger.error("Browser not ready")
            return None
        
        try:
            logger.info(f"Navigating to: {url}")
            
            # Navigate to the page
            response = await self.page.goto(url, wait_until="networkidle")
            
            if not response or response.status >= 400:
                logger.error(f"Failed to load page: {response.status if response else 'No response'}")
                return None
            
            # Wait for page to fully load
            await self.page.wait_for_load_state("networkidle")
            
            # Additional wait for dynamic content
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            # Scroll to load lazy-loaded content
            await self._scroll_page()
            
            # Get the final HTML content
            html_content = await self.page.content()
            
            logger.info(f"Successfully loaded page: {len(html_content)} characters")
            return html_content
            
        except Exception as e:
            logger.error(f"Error loading page {url}: {e}")
            return None
    
    async def _scroll_page(self):
        """Scroll the page to trigger lazy loading"""
        try:
            # Get page height
            page_height = await self.page.evaluate("document.body.scrollHeight")
            
            # Scroll in chunks
            chunk_size = 1000
            current_position = 0
            
            while current_position < page_height:
                await self.page.evaluate(f"window.scrollTo(0, {current_position})")
                await asyncio.sleep(0.5)  # Wait for content to load
                current_position += chunk_size
            
            # Scroll back to top
            await self.page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.warning(f"Error during page scrolling: {e}")
    
    async def _block_resource(self, route):
        """Block unnecessary resources to speed up loading"""
        if route.request.resource_type in ["image", "stylesheet", "font"]:
            await route.abort()
        else:
            await route.continue_()
    
    async def take_screenshot(self, url: str, output_path: str = "screenshot.png") -> bool:
        """
        Take a screenshot of the page (useful for debugging)
        
        Args:
            url: The URL to screenshot
            output_path: Path to save the screenshot
        
        Returns:
            True if successful, False otherwise
        """
        try:
            html_content = await self.get_page_content(url)
            if html_content:
                await self.page.screenshot(path=output_path, full_page=True)
                logger.info(f"Screenshot saved to: {output_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False
    
    async def get_page_info(self, url: str) -> Optional[dict]:
        """
        Get basic page information (title, meta description, etc.)
        
        Args:
            url: The URL to analyze
        
        Returns:
            Dictionary with page information or None if failed
        """
        try:
            html_content = await self.get_page_content(url)
            if not html_content:
                return None
            
            # Extract basic page info
            title = await self.page.title()
            description = await self.page.evaluate("""
                () => {
                    const meta = document.querySelector('meta[name="description"]');
                    return meta ? meta.getAttribute('content') : '';
                }
            """)
            
            return {
                "url": url,
                "title": title,
                "description": description,
                "content_length": len(html_content)
            }
            
        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            return None 