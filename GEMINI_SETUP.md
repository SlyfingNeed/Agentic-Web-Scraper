# Gemini API Setup Guide

## Getting Your Gemini API Key

1. **Visit Google AI Studio**
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with your Google account

2. **Create API Key**
   - Click "Create API Key"
   - Copy the generated API key

3. **Set Up Environment**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your API key:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

## Benefits of Using Gemini

- ✅ **Free Tier**: 15 requests per minute, 1500 requests per day
- ✅ **No Credit Card Required**: Unlike OpenAI
- ✅ **High Quality**: Powered by Google's latest AI models
- ✅ **Reliable**: Google's infrastructure

## Usage Limits

- **Free Tier**: 15 requests/minute, 1500 requests/day
- **Paid Tier**: Higher limits available if needed

## Testing Your Setup

Run the test script to verify everything works:
```bash
python test_api.py
```

## Troubleshooting

If you get API key errors:
1. Make sure the API key is correctly copied
2. Check that the `.env` file is in the project root
3. Verify the API key format (should be a long string)
4. Ensure you're not exceeding the free tier limits 