from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware  # ADD THIS
from pydantic import BaseModel
from strands import Agent, tool  # ADD 'tool' HERE
from strands.session.s3_session_manager import S3SessionManager
import boto3
import json
import logging
import os
import uuid
import uvicorn
import requests

model_id = os.environ.get("MODEL_ID", "us.anthropic.claude-sonnet-4-0-20250514-v1:0")
state_bucket = os.environ.get("STATE_BUCKET", "")
state_prefix = os.environ.get("STATE_PREFIX", "sessions/")

logging.getLogger("strands").setLevel(logging.WARNING)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Logger initialized")

if not state_bucket:
    raise RuntimeError("STATE_BUCKET environment variable must be set")

if state_prefix and not state_prefix.endswith("/"):
    state_prefix = f"{state_prefix}/"

boto_session = boto3.Session()
@tool
def celsius_to_fahrenheit(celsius: float) -> str:
    """Convert Celsius to Fahrenheit
    
    Args:
        celsius: Temperature in Celsius
        
    Returns:
        Formatted string with conversion result
    """
    fahrenheit = round((celsius * 9/5) + 32, 1)
    return f"{celsius}°C = {fahrenheit}°F"

@tool
def fahrenheit_to_celsius(fahrenheit: float) -> str:
    """Convert Fahrenheit to Celsius
    
    Args:
        fahrenheit: Temperature in Fahrenheit
        
    Returns:
        Formatted string with conversion result
    """
    celsius = round((fahrenheit - 32) * 5/9, 1)
    return f"{fahrenheit}°F = {celsius}°C"
@tool
def weather_per_city_3days(city: str) -> str:
    """Get 3-day weather forecast for a city.
    
    Args:
        city: The name of the city
        
    Returns:
        3-day weather forecast
    """
    try:
        # ✅ Create cache key
        #cache_key = f"{city.lower()}_3days"
        
        # ✅ Check cache first
        #cached_data = weather_cache.get(cache_key)
        #if cached_data:
           # logger.info(f"Returning cached 3-day forecast for {city}")
           # return cached_data['formatted_result']
        
        # ✅ Fetch from API if not cached
        logger.info(f"Fetching fresh 3-day forecast for {city}")
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url=url, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        
        # Start with current conditions
        current_condition = weather_data['current_condition'][0]
        result = f"🌤️ Weather Forecast for {city}:\n\n"
        result += f"📍 Current: {current_condition['temp_C']}°C, {current_condition['weatherDesc'][0]['value']}\n"
        result += f"💧 Humidity: {current_condition['humidity']}%\n\n"
        
        # Add 3-day forecast
        result += "📅 3-Day Forecast:\n"
        for i, day in enumerate(weather_data['weather'][:3], 1):
            result += f"\n🗓️  Day {i} ({day['date']}):\n"
            result += f"  🌡️  High: {day['maxtempC']}°C / Low: {day['mintempC']}°C\n"
            result += f"  ☀️  UV Index: {day['uvIndex']}\n"
            
            # Get midday forecast
            noon_forecast = day['hourly'][4] if len(day['hourly']) > 4 else day['hourly'][0]
            result += f"  ☁️  Condition: {noon_forecast['weatherDesc'][0]['value']}\n"
            result += f"  💧 Humidity: {noon_forecast['humidity']}%\n"
        
        # ✅ Store in cache
        #weather_cache.set(cache_key, {
         #   'raw_data': weather_data,
         #   'formatted_result': result,
          #  'city': city
       # })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting 3-day forecast for {city}: {str(e)}")
        return f"❌ Error getting weather for {city}: {str(e)}"


@tool
def weather_per_city(city: str) -> str:
    """Get weather forecast for a city.
    Args:
        city: The name of the city
    """
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url=url)
        response.raise_for_status()
        weather_data = response.json()
        current_condition = weather_data['current_condition'][0]
        
        result = f"Weather in {city}:\n"
        result += f"Current: {current_condition['temp_C']}°C, {current_condition['weatherDesc'][0]['value']}\n"
        result += f"Humidity: {current_condition['humidity']}%\n\n"
        
        return result
    except Exception as e:
        return f"Error getting weather for {city}: {str(e)}"

class ChatRequest(BaseModel):
    prompt: str

def create_agent(session_id: str) -> Agent:
    session_manager_kwargs = {
        "session_id": session_id,
        "bucket": state_bucket,
        "boto_session": boto_session,
    }
    if state_prefix:
        session_manager_kwargs["prefix"] = state_prefix
    
    session_manager = S3SessionManager(**session_manager_kwargs)
    agent = Agent(model=model_id, session_manager=session_manager, tools=[weather_per_city,fahrenheit_to_celsius,fahrenheit_to_celsius,weather_per_city_3days])
    logger.info("Agent initialized for session %s", session_id)
    return agent

app = FastAPI()

# ADD CORS MIDDLEWARE - THIS IS CRITICAL!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Called by the Lambda Adapter to check liveness
@app.get("/")
async def root():
    return {"message": "OK"}

@app.get('/chat')
def chat_history(request: Request):
    session_id = request.cookies.get("session_id", str(uuid.uuid4()))
    agent = create_agent(session_id)

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
    response.set_cookie(key="session_id", value=session_id)
    return response

@app.post('/chat')
async def chat(chat_request: ChatRequest, request: Request):
    session_id = request.cookies.get("session_id", str(uuid.uuid4()))
    agent = create_agent(session_id)
    response = StreamingResponse(
        generate(agent, session_id, chat_request.prompt, request),
        media_type="text/event-stream"
    )
    response.set_cookie(key="session_id", value=session_id)
    return response

async def generate(agent: Agent, session_id: str, prompt: str, request: Request):
    try:
        async for event in agent.stream_async(prompt):
            if await request.is_disconnected():
                logger.info("Client disconnected before completion for session %s", session_id)
                break
            if "complete" in event:
                logger.info("Response generation complete")
            if "data" in event:
                yield f"data: {json.dumps(event['data'])}\n\n"
 
    except Exception as e:
        error_message = json.dumps({"error": str(e)})
        yield f"event: error\ndata: {error_message}\n\n"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))