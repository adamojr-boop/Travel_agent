# Travel Agent API - Progetto Finale

API backend sviluppata con **FastAPI**, **LangChain** e **Pydantic** per la generazione automatizzata e strutturata di piani di viaggio personalizzati, potenziata da ricerche web in tempo reale tramite **Tavily**.

---

## 🛠️ Architettura e Stack Tecnologico

Il progetto si basa su un'architettura ad **agente autonomo** capace di elaborare richieste in linguaggio naturale, raccogliere informazioni aggiornate dal web e restituire un itinerario dettagliato in formato JSON validato.

* **FastAPI**: Framework web asincrono per l'esposizione degli endpoint RESTful (`/api/travel-plan`) e della documentazione OpenAPI/Swagger interattiva (`/docs`).
* **LangChain**: Orchestratore del flusso di lavoro dell'intelligenza artificiale e gestione delle catene di esecuzione (LCEL).
* **OpenAI GPT-4o**: Modello linguistico avanzato utilizzato per il ragionamento, la sintesi delle informazioni e l'organizzazione dell'itinerario.
* **Tavily Search (`langchain-tavily`)**: Motore di ricerca web ottimizzato per gli LLM, impiegato per recuperare dati di mercato in tempo reale (prezzi indicativi, attrazioni, opzioni di volo e alloggio).
* **Pydantic**: Garanzia e validazione rigida dello schema di output dati (**Structured Outputs**).
* **Poetry**: Gestore dell'ambiente virtuale e delle dipendenze del progetto.

---

## Funzionalità e Personalizzazioni Apportate

1. **Routing e Pre-elaborazione con `RunnableLambda`**:
   L'input dell'utente viene processato da un blocco personalizzato `RunnableLambda` che analizza la richiesta e costruisce una query di ricerca ottimizzata per estrarre specificamente voli, alloggi, trasporti e costi aggiornati.
2. **Estensione dello Schema di Viaggio (`schemas.py`)**:
   L'output di Pydantic non si limita a una semplice descrizione testuale, ma restituisce una struttura ricca e finanziariamente trasparente articolata in:
   * **Alloggi Consigliati**: Nomi, tipologie e costi stimati a notte.
   * **Dettaglio Trasporti**: Voli, treni, mezzi locali o noleggi con relative stime di spesa.
   * **Itinerario Giorno per Giorno**: Programma orario dettagliato delle attività con prezzi indicativi delle attrazioni.
   * **Riepilogo Budget Complessivo**: Breakdown aggregato delle spese per persona e gruppo.
3. **Gestione delle Eccezioni e Fallback (Tavily)**:
   Integrazione di blocchi `try-except` con estrazione del messaggio di eccezione `({e})`. Se il servizio di ricerca web è momentaneamente non disponibile, l'agente non va in crash ma attiva un meccanismo di fallback basato sulle stime interne del modello.
4. **Tracing dell'Esecuzione in Tempo Reale**:
   Inserimento di istruzioni di stampa `print` nel codice per monitorare ogni fase dell'elaborazione nella console del terminale (analisi input, costruzione della query, chiamata a Tavily, caricamento dello schema Pydantic e completamento).

---