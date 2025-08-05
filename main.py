from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import asyncio
from typing import List, Dict, Any

from agent import ScrapingAgent
from browser import BrowserManager
from scraper import HTMLScraper

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Web Scraper API",
    description="An intelligent web scraping API that uses AI to understand queries and extract structured data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ScrapeRequest(BaseModel):
    query: str

class ScrapeResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    message: str = ""

# Initialize components
scraping_agent = ScrapingAgent()
browser_manager = BrowserManager()
html_scraper = HTMLScraper()

@app.on_event("startup")
async def startup_event():
    """Initialize browser on startup"""
    await browser_manager.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up browser on shutdown"""
    await browser_manager.cleanup()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI-Powered Web Scraper API is running"}

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_website(request: ScrapeRequest):
    """
    Main scraping endpoint that:
    1. Uses AI to interpret the query and determine scraping strategy
    2. Navigates to the target website
    3. Extracts and structures the data
    """
    try:
        # Step 1: Use AI to interpret the query and get scraping strategy
        scraping_strategy = await scraping_agent.interpret_query(request.query)
        
        if not scraping_strategy.get("url"):
            raise HTTPException(status_code=400, detail="Could not determine target URL from query")
        
        # Step 2: Navigate to the website and get HTML content
        html_content = await browser_manager.get_page_content(scraping_strategy["url"])
        
        if not html_content:
            raise HTTPException(status_code=500, detail="Failed to retrieve page content")
        
        # Step 3: Use AI to extract structured data from HTML
        extracted_data = await scraping_agent.extract_data(
            html_content, 
            scraping_strategy["target_elements"],
            request.query
        )
        
        return ScrapeResponse(
            success=True,
            data=extracted_data,
            message=f"Successfully scraped {len(extracted_data)} items from {scraping_strategy['url']}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "browser": await browser_manager.is_ready(),
            "gemini": scraping_agent.is_ready()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
