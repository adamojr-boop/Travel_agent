import os
import re
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from travel_agent_api.schemas import PianoViaggio

load_dotenv()
logger = logging.getLogger(__name__)

def preparatore_ricerca(input_data: dict) -> dict:
    testo = input_data["input_utente"]
    print("\n--- Analisi input e costruzione query di ricerca ---")
    
    #Pulizia prompt utente
    pattern = r'\b(ciao|buongiorno|salve|per favore|grazie|mi\s+aiuti|puoi\s+aiutarmi)\b'
    testo_pulito = re.sub(pattern, '', testo, flags=re.IGNORECASE)
    testo_pulito = re.sub(r'\s+', ' ', testo_pulito).strip()
    
    if not testo_pulito:
        testo_pulito = testo

    query_ottimizzata = f"voli, hotel consigliati, prezzi e attrazioni principali per: {testo_pulito}"
    print(f"Query generata: '{query_ottimizzata}'")
    
    return {
        "input_utente": testo,
        "query_ricerca": query_ottimizzata
    }

prepara_ricerca_lambda = RunnableLambda(preparatore_ricerca)

def estrai_valore_numerico(stringa_prezzo: str) -> float:
    """Estrae un valore float da una stringa come '15545€' o '1.500,50 €'."""
    if not stringa_prezzo:
        return 0.0
    #Rimuove simboli di valuta e lettere, pulisce i punti delle migliaia e converte la virgola in punto
    numeri_puliti = re.sub(r'[^\d,\.]', '', stringa_prezzo)
    if not numeri_puliti:
        return 0.0
    numeri_puliti = numeri_puliti.replace('.', '').replace(',', '.')
    try:
        return float(numeri_puliti)
    except ValueError:
        return 0.0

def genera_piano_viaggio(richiesta_utente: str, numero_persone: int = 1, budget_massimo: float = None) -> PianoViaggio:
    print("\n--- Avvio Agente di Viaggio Completo ---")
    print(f"Richiesta utente: '{richiesta_utente}' | Partecipanti: {numero_persone} | Budget massimo: {budget_massimo}€")

    dati_preparati = prepara_ricerca_lambda.invoke({"input_utente": richiesta_utente})

    #Gestione e fallback di Tavily
    risultati_ricerca = "Informazioni web non disponibili, fornisci stime di mercato realistiche."
    tavily_key = os.getenv("TAVILY_API_KEY")

    if tavily_key and tavily_key != "inserisci_qui_la_tua_tavily_api_key":
        try:
            tavily_tool = TavilySearch(max_results=5, tavily_api_key=tavily_key)
            print("Avvio ricerca live su Tavily per costi, alloggi e trasporti...")
            risultati_ricerca = tavily_tool.invoke({"query": dati_preparati["query_ricerca"]})
            print("Tavily ha recuperato le informazioni di mercato aggiornate.")
        except Exception as e:
            logger.warning(f"Errore Tavily ({e}), prosieguo con le stime interne.")
    else:
        logger.warning("TAVILY_API_KEY non configurata o non valida. Ricerca web disabilitata (fallback attivo).")

    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    llm_strutturato = llm.with_structured_output(PianoViaggio)
    print("Configurato GPT-4o con lo schema completo PianoViaggio.")

    #Vincoli dinamici basati sugli input dell'utente
    vincoli_extra = f"- Numero partecipanti: {numero_persone} persona/e.\n"
    if budget_massimo:
        vincoli_extra += f"- BUDGET MASSIMO IMPERATIVO: Il 'budget_totale_stimato' NON DEVE IN ALCUN MODO SUPERARE i {budget_massimo}€.\n"
    else:
        vincoli_extra += "- Calcola un budget totale realistico rapportato al numero di persone.\n"

    system_prompt = (
        "Sei un agente di viaggio professionista esperto in pianificazione logistica e finanziaria. "
        "Il tuo compito è creare un piano di viaggio completo che includa:\n"
        "1. Opzioni di volo/trasporto principale e mezzi locali con stime di prezzo reali.\n"
        "2. Opzioni di alloggio dettagliate con costi a notte.\n"
        "3. Itinerario giorno per giorno con costi previsti per le varie attività.\n"
        "4. Riepilogo complessivo del budget preventivato.\n\n"
        "VINCOLI CRITICI:\n"
        f"{vincoli_extra}"
        "Assicurati che i costi totali nel riepilogo riflettano accuratamente il numero di persone indicato."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Richiesta dell'utente: {input_utente}\n\nRisultati live dal Web (Tavily):\n{dati_web}")
    ])

    print("Generazione dell'itinerario finanziario e logistico in corso...")
    
    catena = prompt | llm_strutturato
    risultato = catena.invoke({
        "input_utente": richiesta_utente,
        "dati_web": str(risultati_ricerca)
    })

    #Controllo del budget (Verifica matematica)
    if budget_massimo and risultato.riepilogo_budget and risultato.riepilogo_budget.budget_totale_stimato:
        totale_calcolato = estrai_valore_numerico(risultato.riepilogo_budget.budget_totale_stimato)
        if totale_calcolato > budget_massimo:
            print(f"[ATTENZIONE] Il budget stimato ({totale_calcolato}€) supera il limite massimo ({budget_massimo}€).")
            logger.warning(f"Il budget stimato {totale_calcolato} supera il massimo consentito {budget_massimo}")

    print("Output validato con successo da Pydantic!")
    print(f"Destinazione: {risultato.destinazione} | Budget stimato: {risultato.riepilogo_budget.budget_totale_stimato}")
    print("--- Fine elaborazione ---")

    return risultato