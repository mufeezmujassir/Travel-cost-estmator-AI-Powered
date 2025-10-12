from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create router
router = APIRouter(prefix="/api")

# Pydantic model for chat request
class ChatRequest(BaseModel):
    message: str

# Pydantic model for chat response
class ChatResponse(BaseModel):
    reply: str

# System prompt for the AI assistant
SYSTEM_PROMPT = """You are a friendly and helpful customer service assistant for our travel cost estimation company. 
Give clear, short answers to customer queries. You specialize in helping users with:
- Travel cost estimation questions
- How to use our travel planning system
- Account and subscription issues
- Technical support for our website
- General travel advice

Always be polite, professional, and concise in your responses."""

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Chat endpoint that uses OpenAI GPT-3.5-turbo to generate responses
    """
    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        # Extract the reply from the response
        reply = response.choices[0].message.content.strip()
        
        return ChatResponse(reply=reply)
        
    except openai.APIError as e:
        # Handle OpenAI API errors
        print(f"OpenAI API error: {e}")
        return ChatResponse(reply="Sorry, I'm having trouble responding right now. Please try again later.")
        
    except Exception as e:
        # Handle any other errors
        print(f"Unexpected error in chat endpoint: {e}")
        return ChatResponse(reply="Sorry, I'm having trouble responding right now. Please try again later.")