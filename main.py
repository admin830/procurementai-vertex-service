import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import pandas as pd
import pdfplumber

# --- Config ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "procurementai-473016")
LOCATION = os.getenv("LOCATION", "us-central1")
BUCKET_NAME = os.getenv("BUCKET_NAME", "procurementai-datos")  # tu bucket con PDFs/CSVs

# Origen permitido
ALLOWED_ORIGINS = [
    "https://storage.googleapis.com",
    "https://storage.googleapis.com/procurementai-web"
]

# --- Init Vertex ---
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-2.5-pro")  # modelo por defecto

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

# --- Función para leer archivos ---
def leer_archivo_gcs(nombre_objeto: str) -> str:
    """Detecta tipo de archivo y devuelve contenido de texto"""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(nombre_objeto)

    if nombre_objeto.endswith(".csv"):
        contenido = blob.download_as_text()
        df = pd.read_csv(pd.compat.StringIO(contenido))
        return df.head(20).to_string(index=False)  # solo primeras 20 filas

    elif nombre_objeto.endswith(".pdf"):
        contenido_texto = ""
        with pdfplumber.open(blob.download_as_bytes()) as pdf:
            for page in pdf.pages:
                contenido_texto += page.extract_text() + "\n"
        return contenido_texto[:5000]  # limitamos tamaño

    elif nombre_objeto.endswith(".txt"):
        return blob.download_as_text(errors="ignore")[:5000]

    else:
        raise ValueError("Tipo de archivo no soportado. Solo PDF, CSV, TXT.")

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
        archivos = body.get("files", [])  # lista de archivos en el bucket

        contexto = ""
        for archivo in archivos:
            # quitar prefijo gs://bucket/ si lo incluyes
            nombre_objeto = archivo.split("/", 3)[-1]
            texto = leer_archivo_gcs(nombre_objeto)
            contexto += f"\n--- Contenido de {nombre_objeto} ---\n{texto}\n"

        input_text = f"""
        Contexto de los documentos:
        {contexto}

        Pregunta del usuario:
        {prompt}
        """

        model = GenerativeModel(model_name)
        response = model.generate_content(input_text)

        return {"model_used": model_name, "response": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
