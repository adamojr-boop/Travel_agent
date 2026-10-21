import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from travel_agent_api.agent import genera_piano_viaggio
from travel_agent_api.schemas import PianoViaggio

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Travel Agent API",
    description="API basata su FastAPI e LangChain per la generazione di piani di viaggio strutturati.",
    version="1.0.0"
)

class RichiestaInput(BaseModel):
    messaggio: str = Field(description="La richiesta di viaggio dell'utente")
    numero_persone: int = Field(default=1, ge=1, description="Numero di partecipanti al viaggio (almeno 1)")
    budget_massimo: Optional[float] = Field(default=None, gt=0, description="Budget massimo complessivo in Euro (opzionale)")

@app.get("/")
def home():
    return {"status": "online", "message": "Benvenuto nelle Travel Agent API!"}

@app.post("/api/travel-plan", response_model=PianoViaggio)
def crea_viaggio(dati: RichiestaInput):
    try:
        #Passiamo tutti i parametri validati all'agente
        piano = genera_piano_viaggio(
            richiesta_utente=dati.messaggio,
            numero_persone=dati.numero_persone,
            budget_massimo=dati.budget_massimo
        )
        return piano
    except Exception as e:
        logger.exception("Errore critico durante la generazione del piano di viaggio:")
        raise HTTPException(
            status_code=500,
            detail="Errore interno durante l'elaborazione della richiesta. Riprova più tardi."
        )