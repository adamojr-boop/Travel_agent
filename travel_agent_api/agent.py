import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from travel_agent_api.schemas import PianoViaggio

load_dotenv()

def preparatore_ricerca(input_data: dict) -> dict:
    testo = input_data["input_utente"]
    print(f"\n--- Analisi input e costruzione query di ricerca ---")
    
    #Query mirata a prezzi, trasporti ed alloggi

    query_ottimizzata = f"voli, hotel consigliati, prezzi e attrazioni principali per: {testo}"
    print(f"Query generata: '{query_ottimizzata}'")
    
    return {
        "input_utente": testo,
        "query_ricerca": query_ottimizzata
    }

prepara_ricerca_lambda = RunnableLambda(preparatore_ricerca)

def genera_piano_viaggio(richiesta_utente: str) -> PianoViaggio:
    print("\n--- Avvio Agente di Viaggio Completo ---")
    print(f"Richiesta utente: {richiesta_utente}")

    #Prepariamo le chiavi di ricerca

    dati_preparati = prepara_ricerca_lambda.invoke({"input_utente": richiesta_utente})

    #Ricerca con Tavily(gestione errori e fallback)

    tavily_tool = TavilySearch(max_results=5)
    print("Avvio ricerca live su Tavily per costi, alloggi e trasporti...")
    
    try:
        risultati_ricerca = tavily_tool.invoke({"query": dati_preparati["query_ricerca"]})
        print(f"Tavily ha recuperato le informazioni di mercato aggiornate.")
    except Exception as e:
        print(f"Errore Tavily ({e}), prosieguo con le stime interne.")
        risultati_ricerca = "Informazioni web non disponibili, fornisci stime di mercato realistiche."

    #LLM con Structured Output

    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    llm_strutturato = llm.with_structured_output(PianoViaggio)
    print("Configurato GPT-4o con lo schema completo PianoViaggio (Voli, Alloggi, Prezzi).")

    #Prompt specifico per Travel Agent professionale

    system_prompt = (
        "Sei un agente di viaggio professionista esperto in pianificazione logistica e finanziaria. "
        "Il tuo compito è creare un piano di viaggio completo che includa:\n"
        "1. Opzioni di volo/trasporto principale e mezzi locali con stime di prezzo reali.\n"
        "2. Opzioni di alloggio dettagliate con costi a notte.\n"
        "3. Itinerario giorno per giorno con costi previsti per le varie attività.\n"
        "4. Riepilogo complessivo del budget preventivato.\n"
        "Usa i dati ottenuti dal web per verificare la plausibilità dei costi e rispetta rigorosamente lo schema JSON richiesto."
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

    print("Output validato con successo da Pydantic!")
    print(f"Destinazione: {risultato.destinazione} | Budget complessivo stimato: {risultato.riepilogo_budget.budget_totale_stimato}")
    print("--- Fine elaborazione ---\n")

    return risultato