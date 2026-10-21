from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from travel_agent_api.agent import genera_piano_viaggio
from travel_agent_api.schemas import PianoViaggio

app = FastAPI(
    title="Travel Agent API",
    description="API basata su FastAPI e LangChain per la generazione di piani di viaggio strutturati.",
    version="1.0.0"
)

# Modello per validare l'input che arriva via HTTP POST

class RichiestaInput(BaseModel):
    messaggio: str = Field(description="La richiesta di viaggio dell'utente, es. 'Voglio andare a Tokyo per 5 giorni con un budget medio'")

@app.get("/")
def home():
    return {"status": "online", "message": "Benvenuto nelle Travel Agent API!"}

@app.post("/api/travel-plan", response_model=PianoViaggio)
def crea_viaggio(dati: RichiestaInput):
    try:

        piano = genera_piano_viaggio(dati.messaggio)
        return piano
    except Exception as e:
        print(f"[ERRORE] Si è verificato un problema: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
