from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import os
import uvicorn
from strands import Agent
from pydantic import BaseModel

model_id = os.environ.get("MODEL_ID", "us.anthropic.claude-3-5-haiku-20241022-v1:0")

class ChatRequest(BaseModel):
    prompt: str = "How can I use curl to POST a JSON object with a key `prompt`?"

app = FastAPI()
agent = Agent(model=model_id)

# Called by the Lambda Adapter to check liveness
@app.get("/")
async def root():
    return {"message": "OK"}

@app.get("/hello")
async def hello():
    prompt = "Reply to the user with a friendly greeting."
    return StreamingResponse(
        generate(prompt),
        media_type="text/plain"
    )

@app.post('/chat')
async def chat(request: ChatRequest):
    return StreamingResponse(
        generate(request.prompt),
        media_type="text/plain"
    )

async def generate(prompt: str):
    try:
        async for event in agent.stream_async(prompt):
            if "data" in event:
                yield event["data"]
    except Exception as e:
        yield f"error: {str(e)}"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
