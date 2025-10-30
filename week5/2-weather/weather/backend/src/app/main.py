from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from strands import Agent, tool
from strands.session.s3_session_manager import S3SessionManager
import boto3
import json
import logging
import os
import uuid
import uvicorn
import requests
import traceback

# Configuration
model_id = os.environ.get("MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")
state_bucket = os.environ.get("STATE_BUCKET", "my-weather-app-state")
state_prefix = os.environ.get("STATE_PREFIX", "sessions/")

# Logging configuration
logging.getLogger("strands").setLevel(logging.WARNING)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.info("=== Weather API Starting ===")
logger.info(f"Model ID: {model_id}")
logger.info(f"State Bucket: {state_bucket}")
logger.info(f"State Prefix: {state_prefix}")

# Ensure state prefix ends with /
if state_prefix and not state_prefix.endswith("/"):
    state_prefix = f"{state_prefix}/"

# Initialize boto3 session
try:
    boto_session = boto3.Session()
    logger.info("✓ Boto3 session initialized")
except Exception as e:
    logger.error(f"✗ Failed to initialize boto3 session: {e}")
    raise

 
@tool
def weather_per_city(city: str) -> str:
    """Get weather forecast for a city.
    
    Args:
        city: The name of the city
    """
    logger.info(f"Fetching weather for city: {city}")
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        current_condition = weather_data['current_condition'][0]
        
        # Build a readable forecast string
        result = f"Weather in {city}:\n"
        result += f"Current: {current_condition['temp_C']}°C, {current_condition['weatherDesc'][0]['value']}\n"
        result += f"Humidity: {current_condition['humidity']}%\n"
        
        logger.info(f"✓ Successfully fetched weather for {city}")
        return result
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching weather for {city}: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error getting weather for {city}: {str(e)}"
        logger.error(error_msg)
        return error_msg


class ChatRequest(BaseModel):
    prompt: str


def create_agent(session_id: str) -> Agent:
    """Create an agent with session management."""
    logger.info(f"Creating agent for session: {session_id}")
    
    try:
        session_manager_kwargs = {
            "session_id": session_id,
            "bucket": state_bucket,
            "boto_session": boto_session,
        }
        if state_prefix:
            session_manager_kwargs["prefix"] = state_prefix
        
        session_manager = S3SessionManager(**session_manager_kwargs)
        agent = Agent(
            model=model_id, 
            session_manager=session_manager, 
            tools=[weather_per_city]
        )
        logger.info(f"✓ Agent created successfully for session {session_id}")
        return agent
    except Exception as e:
        logger.error(f"✗ Failed to create agent: {e}")
        logger.error(traceback.format_exc())
        raise


# Initialize FastAPI app
app = FastAPI(
    title="Weather API",
    description="AI-powered weather reporting API",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("✓ CORS middleware configured")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "OK", "status": "healthy", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "model": model_id,
        "bucket": state_bucket,
        "timestamp": str(boto_session.client('sts').get_caller_identity())
    }


@app.get('/chat')
async def chat_history(request: Request):
    """Get chat history for the current session."""
    session_id = request.cookies.get("session_id", str(uuid.uuid4()))
    logger.info(f"Fetching chat history for session: {session_id}")
    
    try:
        agent = create_agent(session_id)

        # Filter messages to only include first text content
        filtered_messages = []
        for message in agent.messages:
            if (message.get("content") and 
                len(message["content"]) > 0 and 
                "text" in message["content"][0]):
                filtered_messages.append({
                    "role": message["role"],
                    "content": [{
                        "text": message["content"][0]["text"]
                    }]
                })
     
        response = Response(
            content=json.dumps({
                "messages": filtered_messages,
            }),
            media_type="application/json",
        )
        response.set_cookie(key="session_id", value=session_id, samesite="none", secure=True)
        logger.info(f"✓ Returned {len(filtered_messages)} messages")
        return response
    except Exception as e:
        logger.error(f"✗ Error fetching chat history: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": "Failed to fetch chat history"}
        )


@app.post('/chat')
async def chat(chat_request: ChatRequest, request: Request):
    """Send a message and stream the response."""
    session_id = request.cookies.get("session_id", str(uuid.uuid4()))
    logger.info(f"New chat request for session {session_id}: {chat_request.prompt[:50]}...")
    
    try:
        agent = create_agent(session_id)
        response = StreamingResponse(
            generate(agent, session_id, chat_request.prompt, request),
            media_type="text/event-stream"
        )
        response.set_cookie(key="session_id", value=session_id, samesite="none", secure=True)
        return response
    except Exception as e:
        logger.error(f"✗ Error in chat endpoint: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": "Failed to process chat request"}
        )


async def generate(agent: Agent, session_id: str, prompt: str, request: Request):
    """Generate streaming response from the agent."""
    try:
        logger.info(f"Starting generation for session {session_id}")
        async for event in agent.stream_async(prompt):
            if await request.is_disconnected():
                logger.info(f"Client disconnected for session {session_id}")
                break
                
            if "complete" in event:
                logger.info("✓ Response generation complete")
                
            if "data" in event:
                yield f"data: {json.dumps(event['data'])}\n\n"
 
    except Exception as e:
        logger.error(f"✗ Error during generation: {e}")
        logger.error(traceback.format_exc())
        error_message = json.dumps({
            "error": str(e),
            "type": "generation_error"
        })
        yield f"event: error\ndata: {error_message}\n\n"


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "detail": "An unexpected error occurred",
            "path": str(request.url)
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )