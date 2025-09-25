import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import pandas as pd
import pdfplumber
import io

# --- Config ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "procurementai-473016")
LOCATION = os.getenv("LOCATION", "us-central1")
BUCKET_NAME = os.getenv("BUCKET_NAME", "procurementai-data")  # bucket de los documentos

# Origen permitido (tu web estática)
ALLOWED_ORIGINS = [
    "https://storage.googleapis.com",
    "https://storage.googleapis.com/procurementai-web"
]

# --- Init Vertex ---
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-2.5-pro")

# --- Init FastAPI ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente GCS
storage_client = storage.Client()

# --- Función para leer UN archivo ---
def leer_archivo_gcs(blob) -> str:
    """Detecta tipo de archivo y devuelve contenido en texto"""
    nombre = blob.name

    if nombre.endswith(".csv"):
        contenido = blob.download_as_text()
        df = pd.read_csv(io.StringIO(contenido))
        return df.head(20).to_string(index=False)  # solo primeras filas

    elif nombre.endswith(".pdf"):
        contenido_texto = ""
        with pdfplumber.open(io.BytesIO(blob.download_as_bytes())) as pdf:
            for page in pdf.pages:
                contenido_texto += page.extract_text() or ""
        return contenido_texto[:5000]

    elif nombre.endswith(".txt"):
        return blob.download_as_text(errors="ignore")[:5000]

    else:
        return ""  # ignoramos tipos no soportados

# --- Endpoints ---
@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/generate")
async def generate(request: Request):
    try:
        body = await request.json()
        prompt = body.get("prompt", "")
        model_name = body.get("model") or "gemini-2.5-pro"

        # --- Barrer todo el bucket ---
        bucket = storage_client.bucket(BUCKET_NAME)
        blobs = bucket.list_blobs()

        contexto = ""
        for blob in blobs:
            texto = leer_archivo_gcs(blob)
            if texto:
                contexto += f"\n--- Contenido de {blob.name} ---\n{texto}\n"

        input_text = f"""
        Contexto de los documentos (PDF/CSV/TXT) en el bucket {BUCKET_NAME}:
        {contexto}

        Pregunta del usuario:
        {prompt}
        """

        model = GenerativeModel(model_name)
        response = model.generate_content(input_text)

        return {"model_used": model_name, "response": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
