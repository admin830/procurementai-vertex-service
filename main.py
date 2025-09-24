from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import aiplatform

app = FastAPI()

# Modelo de la petición
class PromptRequest(BaseModel):
    prompt: str

# Inicializar Vertex AI
aiplatform.init(location="us-central1")  # Ajusta si usas otra región

@app.post("/generate")
async def generate_text(request: PromptRequest):
    try:
        # Cliente de Gemini
        model = aiplatform.GenerativeModel("gemini-1.5-flash")

        # Llamar al modelo
        response = model.generate_content(request.prompt)

        return {"response": response.text}

    except Exception as e:
        return {"error": str(e)}
