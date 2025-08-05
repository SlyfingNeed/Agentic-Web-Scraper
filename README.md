# AI-Powered Web Scraper API

An intelligent web scraping API that uses AI to understand natural language queries and extract structured data from websites. Built with FastAPI, Google Gemini, Playwright, and BeautifulSoup.

## Transparency Acknowledgement

This project was developed with the assistance of AI tools such as Cursor and ChatGPT for rapid prototyping. Final logic and structure were reviewed and modified by the developer

## Features

- **AI-Powered Query Interpretation**: Uses Google Gemini to understand what to scrape from natural language queries
- **JavaScript Rendering**: Uses Playwright to handle dynamic content and SPAs
- **Structured Data Extraction**: Extracts articles, links, headlines, and metadata
- **Async Processing**: Built with async/await for better performance
- **CORS Support**: Ready for frontend integration
- **Production Ready**: Includes error handling, logging, and health checks

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

### 3. Set Up Environment Variables

Copy the example environment file and add your OpenAI API key:

```bash
cp env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 4. Run the API

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Usage

### Scrape Content

**POST** `/scrape`

Request body:
```json
{
  "query": "Scrape Bitcoin articles from CNN"
}
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "title": "Bitcoin reaches new all-time high",
      "link": "https://www.cnn.com/2024/01/15/bitcoin-high",
      "summary": "Bitcoin surged to a new record high as institutional adoption continues...",
      "date": "2024-01-15",
      "source": "CNN",
      "category": "Cryptocurrency"
    }
  ],
  "message": "Successfully scraped 5 items from https://www.cnn.com"
}
```

### Health Check

**GET** `/health`

Returns the status of all components:
```json
{
  "status": "healthy",
  "components": {
    "browser": true,
    "openai": true
  }
}
```

## Supported Query Types

The AI can understand various types of scraping requests:

- **News Articles**: "Get latest tech news from TechCrunch"
- **Product Information**: "Scrape iPhone reviews from Amazon"
- **Social Media**: "Get trending posts from Reddit"
- **Blog Posts**: "Extract articles from Medium about AI"
- **Custom Websites**: "Scrape job listings from Indeed"

## Architecture

### Components

1. **`main.py`** - FastAPI application with endpoints and middleware
2. **`agent.py`** - Google Gemini agent for query interpretation and data extraction
3. **`browser.py`** - Playwright browser manager for page loading
4. **`scraper.py`** - BeautifulSoup HTML parser and data extractor

### Flow

1. **Query Interpretation**: AI analyzes the natural language query to determine:
   - Target website URL
   - What elements to scrape
   - Scraping strategy

2. **Page Loading**: Playwright loads the page and renders JavaScript

3. **Data Extraction**: AI extracts structured data from the HTML content

4. **Response**: Returns formatted JSON with extracted data

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Required |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `HEADLESS` | Run browser in headless mode | `true` |
| `BROWSER_TIMEOUT` | Browser timeout (ms) | `30000` |

### Customization

You can customize the scraping behavior by modifying:

- **Website mappings** in `agent.py` for common sites
- **CSS selectors** in `scraper.py` for different content types
- **Browser settings** in `browser.py` for different environments

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Testing

Test the API with curl:

```bash
curl -X POST "http://localhost:8000/scrape" \
     -H "Content-Type: application/json" \
     -d '{"query": "Get latest news from BBC"}'
```

## Production Deployment

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
```

### Environment Setup

For production, ensure:
- Set `HEADLESS=true` for server environments
- Configure proper CORS origins
- Set up logging and monitoring
- Use environment-specific API keys

## Troubleshooting

### Common Issues

1. **Playwright Installation**: Make sure to run `playwright install chromium`
2. **Gemini API Key**: Verify your API key is valid
3. **Browser Issues**: Check if running in headless mode is required for your environment
4. **Memory Usage**: Large pages may require more memory allocation

### Logs

Check the application logs for detailed error information. The API includes comprehensive logging for debugging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 