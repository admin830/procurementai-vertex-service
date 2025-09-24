import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel

app = FastAPI()

# Inicializar Vertex AI
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Modelo generativo
model = GenerativeModel("gemini-1.5-flash")

class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_text(request: PromptRequest):
    try:
        response = model.generate_content(request.prompt)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Vertex AI Cloud Run service is up!"}
