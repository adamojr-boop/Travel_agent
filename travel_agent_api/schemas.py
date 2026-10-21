from pydantic import BaseModel, Field
from typing import List, Optional

class OpzioneAlloggio(BaseModel):
    nome: str = Field(description="Nome dell'hotel, B&B o struttura consigliata")
    tipologia: str = Field(description="Es. Hotel 3 stelle, Ostello, Appartamento, Resort")
    prezzo_stimato_notte: str = Field(description="Costo indicativo a notte (es. '120€/notte')")
    note: Optional[str] = Field(default=None, description="Pro/Contro o posizione strategica")

class DettaglioTrasporto(BaseModel):
    tipologia: str = Field(description="Volo, Treno, Pass Metro, Noleggio Auto, ecc.")
    descrizione: str = Field(description="Dettagli sulla tratta, compagnia o pass consigliato")
    costo_stimato: str = Field(description="Costo stimato complessivo o a persona")

class AttivitaGiorno(BaseModel):
    ora: str = Field(description="Orario indicativo dell'attività, es. '09:00'")
    titolo: str = Field(description="Titolo sintetico dell'attività")
    descrizione: str = Field(description="Dettagli di cosa fare, luoghi e consigli")
    costo_stimato: Optional[str] = Field(default="Gratuito", description="Costo stimato dell'ingresso o attività")

class GiornoItinerario(BaseModel):
    giorno: int = Field(description="Numero del giorno, es. 1")
    titolo_giorno: str = Field(description="Tema principale o zona visitata")
    attivita: List[AttivitaGiorno] = Field(description="Programma dettagliato della giornata")

class RiepilogoCosti(BaseModel):
    totale_voli_trasporti: str = Field(description="Stima totale per i trasporti")
    totale_alloggi: str = Field(description="Stima totale per il soggiorno/hotel")
    totale_attivita_cibo: str = Field(description="Stima indicativa per pasti e attrazioni")
    budget_totale_stimato: str = Field(description="Somma totale complessiva per persona o gruppo")

class PianoViaggio(BaseModel):
    destinazione: str = Field(description="Città/Paese o itinerario generale di destinazione")
    durata_giorni: int = Field(description="Numero totale di giorni di viaggio")
    periodo_consigliato: Optional[str] = Field(default=None, description="Note sulle date/stagione richieste")
    sintesi: str = Field(description="Panoramica e presentazione generale del viaggio")
    alloggi_consigliati: List[OpzioneAlloggio] = Field(description="2-3 opzioni di alloggio in linea col budget")
    trasporti_e_spostamenti: List[DettaglioTrasporto] = Field(description="Voli, treni interni, mezzi locali")
    itinerario: List[GiornoItinerario] = Field(description="Programma giorno per giorno con prezzi attrazioni")
    riepilogo_budget: RiepilogoCosti = Field(description="Breakdown finale di tutti i costi previsti")