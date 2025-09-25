import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import vertexai
from vertexai.generative_models import GenerativeModel

# --- Config ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "procurementai-473016")
LOCATION = os.getenv("LOCATION", "us-central1")

# Origenes permitidos: RECOMENDADO poner la URL exacta de tu bucket
# Ejemplo: "https://storage.googleapis.com/procurementai-web"
# Para prueba rápida puedes usar "*" (ver nota).
ALLOWED_ORIGINS = os.getenv("https://storage.googleapis.com/procurementai-web/index.html", "https://storage.googleapis.com/procurementai-web")  

# --- Init Vertex ---
vertexai.init(project=PROJECT_ID, location=LOCATION)

app = FastAPI()

# CORS: si ALLOWED_ORIGINS == "*" entonces setear allow_credentials=False
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

# Modelo por defecto (puedes cambiar)
DEFAULT_MODEL = "gemini-2.5-pro"

class PromptPayload:
    # simple parsing without pydantic for brevity
    pass

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
