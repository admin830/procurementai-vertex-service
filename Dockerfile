# Imagen base ligera con Python
FROM python:3.11-slim

# Crear directorio de la app
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY main.py .

# Exponer el puerto
EXPOSE 8080

# Comando para ejecutar con Uvicorn en Cloud Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
