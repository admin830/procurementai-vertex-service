import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import vertexai
from vertexai.generative_models import GenerativeModel

# --- Configuración ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "procurementai-473016")
LOCATION = os.getenv("LOCATION", "us-central1")

# 🚨 IMPORTANTE: pon aquí la URL exacta de tu frontend en Storage
# Ejemplo de bucket público:
#   https://storage.googleapis.com/procurementai-web/index.html
#   https://storage.googleapis.com/procurementai-web
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://storage.googleapis.com/procurementai-web"
)

# --- Inicializa Vertex ---
vertexai.init(project=PROJECT_ID, location=LOCATION)

app = FastAPI()

# --- Configura CORS ---
if ALLOWED_ORIGINS.strip() == "*":
    allow_credentials = False
    origins = ["*"]
else:
    allow_credentials = True
    origins = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
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

        return {
            "model_used": model_name,
            "response": response.text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
