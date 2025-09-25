# meta-project (V3.1 Scaffold)

Projeto V3.1 — scaffold inicial com arquitetura proposta.  
Demo project com MockAdapter e GUI de Métricas (UX + spinner).

## Como usar (dev)

- Crie um venv com Python 3.11
- Instale dependências: `pip install -r requirements.txt`
- Rodar FastAPI (etapa4): `uvicorn backend.etapa4_service.main:app --reload`
- Rodar GUI: `python -m app.gui`
- Rodar smoke test: `pytest tests/smoke_test.py -q`

Este repositório contém esqueletos para:
- GUI (Tkinter)  
- JobManager  
- Adapter mock  
- Models SQLAlchemy  
- Serviço FastAPI para Etapa 4