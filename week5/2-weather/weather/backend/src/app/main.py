from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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

model_id = os.environ.get("MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")
state_bucket = os.environ.get("STATE_BUCKET", "my-default-bucket")
state_prefix = os.environ.get("STATE_PREFIX", "sessions/")

logging.getLogger("strands").setLevel(logging.WARNING)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Logger initialized")

if state_prefix and not state_prefix.endswith("/"):
    state_prefix = f"{state_prefix}/"

boto_session = boto3.Session()

 
@tool
def weather_per_city(city: str) -> str:
    """Get weather forecast for a city.
    
    Args:
        city: The name of the city
    """
    logger.info(f"🔧 TOOL CALLED: weather_per_city for city='{city}'")  # DEBUG
    try:
        url = f"https://wttr.in/{city}?format=j1"
        logger.info(f"📡 Fetching weather from: {url}")  # DEBUG
        response = requests.get(url=url, timeout=10)
        response.raise_for_status()
        
        weather_data = response.json()
        current_condition = weather_data['current_condition'][0]
        
        # Build a readable forecast string
        result = f"Weather in {city}:\n"
        result += f"Current: {current_condition['temp_C']}°C, {current_condition['weatherDesc'][0]['value']}\n"
        result += f"Humidity: {current_condition['humidity']}%\n\n"
        
        logger.info(f"✅ TOOL SUCCESS: Got weather data for {city}")  # DEBUG
        return result
    except Exception as e:
        error_msg = f"Error getting weather for {city}: {str(e)}"
        logger.error(f"❌ TOOL ERROR: {error_msg}")  # DEBUG
        return error_msg


class ChatRequest(BaseModel):
    prompt: str


def create_agent(session_id: str) -> Agent:
    logger.info(f"Creating agent for session: {session_id}")
    session_manager_kwargs = {
        "session_id": session_id,
        "bucket": state_bucket,
        "boto_session": boto_session,
    }
    if state_prefix:
        session_manager_kwargs["prefix"] = state_prefix
    
    session_manager = S3SessionManager(**session_manager_kwargs)
    
    # Create agent with the weather tool
    agent = Agent(
        model=model_id, 
        session_manager=session_manager, 
        tools=[weather_per_city]  # ✅ Tool is registered here
    )
    logger.info(f"✅ Agent initialized with weather_per_city tool for session {session_id}")
    return agent


app = FastAPI()

# CORS MIDDLEWARE - CRITICAL FOR BROWSER ACCESS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("✅ CORS middleware configured")

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "OK", "version": "1.0", "tools": ["weather_per_city"]}


@app.get('/chat')
def chat_history(request: Request):
    session_id = request.cookies.get("session_id", str(uuid.uuid4()))
    logger.info(f"📖 Chat history requested for session: {session_id}")
    
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
     
        logger.info(f"✅ Returning {len(filtered_messages)} messages")
        response = Response(
            content=json.dumps({
                "messages": filtered_messages,
            }),
            media_type="application/json",
        )
        response.set_cookie(key="session_id", value=session_id, samesite="none", secure=True)
        return response
    except Exception as e:
        logger.error(f"❌ Error in chat_history: {e}")
        raise


@app.post('/chat')
async def chat(chat_request: ChatRequest, request: Request):
    session_id = request.cookies.get("session_id", str(uuid.uuid4()))
    logger.info(f"💬 New chat message for session {session_id}")
    logger.info(f"📝 User prompt: {chat_request.prompt[:100]}...")
    
    try:
        agent = create_agent(session_id)
        response = StreamingResponse(
            generate(agent, session_id, chat_request.prompt, request),
            media_type="text/event-stream"
        )
        response.set_cookie(key="session_id", value=session_id, samesite="none", secure=True)
        return response
    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {e}")
        raise


async def generate(agent: Agent, session_id: str, prompt: str, request: Request):
    """Generate streaming response from the agent."""
    logger.info(f"🚀 Starting generation for session {session_id}")
    try:
        async for event in agent.stream_async(prompt):
            if await request.is_disconnected():
                logger.info(f"Client disconnected for session {session_id}")
                break
            
            # Log tool use events
            if "data" in event:
                event_data = event["data"]
                if event_data.get("type") == "tool_use":
                    logger.info(f"🔧 Tool use detected: {event_data.get('name')}")
                elif event_data.get("type") == "tool_result":
                    logger.info(f"✅ Tool result received")
                    
            if "complete" in event:
                logger.info("✅ Response generation complete")
                
            if "data" in event:
                yield f"data: {json.dumps(event['data'])}\n\n"
 
    except Exception as e:
        logger.error(f"❌ Error during generation: {e}")
        error_message = json.dumps({"error": str(e)})
        yield f"event: error\ndata: {error_message}\n\n"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    logger.info(f"🚀 Starting server on port {port}")
    logger.info(f"📍 Model: {model_id}")
    logger.info(f"🪣 S3 Bucket: {state_bucket}")
    logger.info(f"🔧 Tools: weather_per_city")
    uvicorn.run(app, host="0.0.0.0", port=port)