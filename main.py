import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import vertexai
from vertexai.generative_models import GenerativeModel

# --- Config ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "procurementai-473016")
LOCATION = os.getenv("LOCATION", "us-central1")

# Origen permitido: URL de tu bucket web estático
# Muy importante: NO incluyas el /index.html al final
ALLOWED_ORIGINS = [
    "https://storage.googleapis.com",   # dominio base
    "https://storage.googleapis.com/procurementai-web"  # bucket
]

# --- Init Vertex ---
vertexai.init(project=PROJECT_ID, location=LOCATION)

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,   # debe estar en False si usas "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo por defecto
DEFAULT_MODEL = "gemini-2.5-pro"

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/generate")
async def generate(request: Request):
    try:
        body = await request.json()
        prompt = body.get("prompt", "")
        model_name = body.get("model") or DEFAULT_MODEL

        model = GenerativeModel(model_name)
        response = model.generate_content(prompt)

        return {"model_used": model_name, "response": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
