from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import aiplatform

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/ask")
def ask_vertex(req: PromptRequest):
    # Inicializa Vertex
    aiplatform.init(project="PROJECT_ID", location="us-central1")
    
    # Modelo generativo (Gemini)
    model = aiplatform.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(req.prompt)

    return {"response": response.text}
