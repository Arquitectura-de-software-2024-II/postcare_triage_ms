from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import os
import uvicorn

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

app = FastAPI()

# Configurar la clave de API de OpenAI desde la variable de entorno
api_key = os.getenv('GEMINI_API_KEY')

class SintomasRequest(BaseModel):
    sintomas: list[str]

def obtener_diagnostico(sintomas):
    prompt = f"Genera una valoracion Prioridad I: prioridad absoluta con atención inmediata y sin demora. Prioridad: situaciones muy urgentes de riesgo vital, inestabilidad o dolor muy intenso. Demora de asistencia médica hasta 15 minutos. Prioridad III: urgente pero estable con potencial riesgo vital que probablemente exige pruebas diagnósticas y/o terapéuticas. Demora máxima de 60 minutos. Prioridad IV: urgencia menor, potencialmente sin riesgo vital para el paciente. Demora máxima de 120 minutos., retorna unicamente en esta forma: (PRIORIDAD <<letra romana de la prioridad>>)  {sintomas}"
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    response = requests.post(endpoint, headers=headers, params={"key": api_key}, json=data)
    json_content = response.json()
    diagnostico = json_content.get('candidates', [])[0].get('content').get('parts')
    return diagnostico

@app.post("/diagnostico")
async def diagnostico(request: SintomasRequest):
    sintomas_str = ', '.join(request.sintomas)
    diagnostico = obtener_diagnostico(sintomas_str)
    return {"diagnostico": diagnostico}

@app.post("/seguimiento")
async def seguimiento(request: SintomasRequest):
    sintomas_str = ', '.join(request.sintomas)
    prompt = f"Recomienda acciones para los siguientes síntomas postoperatorios: {sintomas_str}"
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    response = requests.post(endpoint, headers=headers, params={"key": api_key}, json=data)
    json_content = response.json()
    recomendaciones = json_content["contents"][0]["parts"][0]["text"]
    return {"recomendaciones": recomendaciones}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)