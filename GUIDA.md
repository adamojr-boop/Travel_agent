# Guida all'avvio/test

[Dependencies]
-> poetry install

[Variables/Secrets]
-> OPENAI_API_KEY=inserisci_qui_la_tua_openai_api_key
   TAVILY_API_KEY=inserisci_qui_la_tua_tavily_api_key

[Start]
-> poetry run uvicorn travel_agent_api.main:app --reload