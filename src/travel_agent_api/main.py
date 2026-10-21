import logging
import re
from typing import Optional, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
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
    # Accettiamo sia float che str (es. "5 000" o "5.000€") convertendoli in automatico
    budget_massimo: Optional[Union[float, str]] = Field(default=None, description="Budget massimo complessivo in Euro (opzionale)")

    @field_validator('budget_massimo', mode='before')
    @classmethod
    def pulisci_budget(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, (int, float)):
            if v <= 0:
                raise ValueError("Il budget deve essere maggiore di zero")
            return float(v)
        if isinstance(v, str):
            # Rimuove spazi, simboli di valuta, punti delle migliaia e converte la virgola in punto
            pulito = re.sub(r'[^\d,\.]', '', v).replace('.', '').replace(',', '.')
            if not pulito:
                return None
            valore = float(pulito)
            if valore <= 0:
                raise ValueError("Il budget deve essere maggiore di zero")
            return valore
        return v

@app.get("/")
def home():
    return {"status": "online", "message": "Benvenuto nelle Travel Agent API!"}

@app.post("/api/travel-plan", response_model=PianoViaggio)
def crea_viaggio(dati: RichiestaInput):
    try:
        # Passiamo tutti i parametri validati all'agente
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