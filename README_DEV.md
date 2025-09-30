# README_DEV — Projeto Scrapers V3.1

## 🎯 Objetivo
Estamos construindo uma **suíte de scrapers** dividida em 3 módulos independentes:
1. **Scraper de Keywords**
2. **Scraper de Anúncios**
3. **Scraper de Domínios**

Cada scraper tem três etapas:
- **Configurações**: navegador headless, credenciais, planilha, parâmetros específicos.
- **Input**: carregar TXT/CSV ou dados da etapa anterior (keywords, anúncios, domínios).
- **Execução**: rodar o scraping, gerar CSV, log e metadados (`run_id`).

O **Monitor** é compartilhado entre todos os scrapers, exibindo runs com metadados e preview de CSV/log.

---

## 🏗 Arquitetura

### Backend (FastAPI)
- `routes_keywords.py` → endpoints `/keywords/*`
- `routes_ads.py` → endpoints `/ads/*`
- `routes_domains.py` → endpoints `/domains/*`
- `routes_monitor.py` → endpoints `/monitor/*` (compartilhado)

Cada `/run` gera:
- `runs/<run_id>.json` (metadados: tipo, start, end, duração, count)
- `runs/<run_id>.done` (sentinela de conclusão)
- `data/<type>-<run_id>.csv`
- `logs/<type>-<run_id>.log`

### Frontend (GUI Tkinter)
- `gui.py` → GUI principal com abas
- `gui_keywords.py` → aba Keywords
- `gui_ads.py` → aba Anúncios
- `gui_domains.py` → aba Domínios
- Monitor tab → Treeview com colunas (`run_id`, `type`, `completed_at`, `duration`, `count`), preview CSV/log, ordenação, limpar histórico, testar conexão.

---

## 🔧 Recursos já implementados
- Execução com `run_id` e artefatos por run.
- Monitor com preview de CSV/log, ordenação por colunas (▲/▼), limpar histórico, testar conexão.
- GUI modular com abas.
- Testes automatizados (`test_monitor_endpoints.py`).

---

## 🚀 Próximos passos
- [ ] Conectar botões de execução de cada aba aos endpoints correspondentes.
- [ ] Garantir que o Monitor mostre runs de todos os scrapers (campo `type`).
- [ ] Unificar a aba de Configurações no futuro (uma só config global).
- [ ] Melhorar UX do preview CSV (modal interno em vez de abrir Explorer).
- [ ] Adicionar testes unitários para cada scraper.

---

## 💡 Instruções para Copilot
- Sempre sugerir código modularizado por scraper (keywords, ads, domains).
- Reaproveitar funções utilitárias já existentes (save_csv, logs, run_id).
- Usar `type` nos metadados para diferenciar runs no Monitor.
- GUI deve manter padrão: Config → Input → Execução em cada aba.
- Evitar duplicação de lógica: se algo é comum, mover para `utils/`.

---

## 🖥️ Setup rápido (Windows PowerShell)

Passos mínimos para configurar o ambiente de desenvolvimento no Windows e rodar testes.

1) Criar e ativar virtualenv:

```powershell
cd "C:\Users\Felipe Augusto\Documents\Projeto V3.1"
python -m venv .venv
# Ativar (padrão PowerShell):
.\.venv\Scripts\Activate.ps1
# Se PowerShell bloquear execução de scripts temporariamente na sessão atual:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# Em alternativa, você pode usar o executável do venv sem ativar:
# .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

2) Instalar dependências:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3) (Opcional) Instalar navegadores para Playwright (se for rodar testes E2E que abrem browser):

```powershell
.\.venv\Scripts\python.exe -m playwright install
```

4) Rodar testes:

```powershell
# Rodar suíte completa
.\.venv\Scripts\python.exe -m pytest -q

# Rodar testes específicos
.\.venv\Scripts\python.exe -m pytest tests/test_api_integration.py -q
```

5) Rodar o backend/gui:

```powershell
# Usar launcher (GUI com botões) ou rodar uvicorn diretamente
python launcher.py
# ou
.\.venv\Scripts\python.exe -m uvicorn backend.etapa4_service.main:app --reload
```

### Notas rápidas
- Se `Activate.ps1` falhar por causa da ExecutionPolicy, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` na sessão atual.
- Adicionei `httpx` em `requirements.txt` para corrigir falha no `TestClient` dos testes.
- Resultado da suíte local: `13 passed`.

---

## Teste rápido: modo CLI do `launcher.py`

O `launcher.py` agora suporta duas flags de linha de comando úteis para testes rápidos do ciclo start→stop do backend:

- `--auto-start` — inicia o backend automaticamente ao abrir o launcher.
- `--auto-stop-seconds=N` — quando usado junto com `--auto-start`, agenda um `stop` após N segundos.

Exemplo (PowerShell):

```powershell
# Inicia o launcher, que por sua vez inicia o backend; o backend será parado após 5 segundos
.\.venv\Scripts\python.exe launcher.py --auto-start --auto-stop-seconds=5
```

Comportamento e observações:
- O servidor escreve um PID file em `logs/uvicorn.pid` ao iniciar; o `launcher` usa esse arquivo para identificar o processo quando pede `stop`.
- Se o processo do servidor for terminado externamente, o `launcher` tentará limpar o PID stale na próxima inicialização.
- A checagem de existência de PIDs usa `psutil` se disponível, mas o código está protegido por `try/except` — `psutil` é opcional.

Nota sobre `psutil`:

- Recomendamos instalar `psutil` em ambientes de desenvolvimento/CI para checagens de PID mais confiáveis. Você pode instalá-lo com:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

O projeto funciona sem `psutil`, mas o launcher fará verificações mais robustas quando ele estiver disponível.

Use este modo para um smoke test rápido: iniciar o launcher em modo auto, checar `http://127.0.0.1:8000/health`, e confirmar que o PID file é removido quando o launcher para o backend.

---

## 🔬 Smoke test integrado (start → /health → stop)

Use este procedimento para validar o ciclo completo de start→health→stop usando o modo CLI do `launcher.py`.

Passos (PowerShell, no diretório do projeto):

```powershell
# 1) Inicie o launcher em modo auto (backend será parado automaticamente após 8 segundos)
.\.venv\Scripts\python.exe launcher.py --auto-start --auto-stop-seconds=8

# 2) Em outra sessão (ou logo após iniciar), verifique o endpoint de health
Start-Sleep -s 2
Invoke-WebRequest -UseBasicParsing -Uri http://127.0.0.1:8000/health -TimeoutSec 5 | Select-Object -ExpandProperty Content

# 3) Cheque que o PID file foi criado imediatamente após o start
Get-Content .\logs\uvicorn.pid

# 4) Aguarde o auto-stop completar (8s + margem) e confirme que o PID file foi removido
Start-Sleep -s 10
if (Test-Path .\logs\uvicorn.pid) { Write-Output "PID_FILE_EXISTS" } else { Write-Output "PID_FILE_REMOVED" }
```

O resultado esperado:
- A chamada a `/health` retorna um payload JSON (ou texto simples) indicando que o backend está saudável.
- `logs/uvicorn.pid` é criado logo após o start e contém o PID do processo do uvicorn.
- Após o auto-stop, `logs/uvicorn.pid` não existe mais.

Notas:
- Se a checagem de `/health` falhar, cole o conteúdo de `logs/server.err` e `logs/server.log` para diagnóstico.
- Em CI recomendamos aumentar `--auto-stop-seconds` se o ambiente do runner for mais lento.

---

## 🗺️ Roadmap / Checklist (curto prazo)

- [x] Dockerfile mínimo criado
- [ ] CI: workflow para buildar imagem e rodar testes dentro do container
- [ ] Deploy básico: escolher destino (Heroku / Railway / VM) e criar pipeline
- [ ] Integração Codecov: adicionar step no CI e configurar `CODECOV_TOKEN` (secret)
- [ ] Documentar contrato de erro (`runs failed`) — exemplos JSON
- [ ] Validar imagem localmente (requer Docker local)

---

## ⚙️ Usando `UVICORN_PORT` / `--port` para testes locais

Para facilitar smoke tests locais em portas alternativas (evitando conflitos), `scripts/start_uvicorn_bg.py` aceita:

- variável de ambiente `UVICORN_PORT` (ex.: `8001`), ou
- argumento CLI `--port=8001`.

Exemplos (PowerShell):

```powershell
# Usando CLI
.\.venv\Scripts\python.exe scripts\start_uvicorn_bg.py --port=8001

# Usando variável de ambiente
$env:UVICORN_PORT = '8002'
.\.venv\Scripts\python.exe scripts\start_uvicorn_bg.py
```

Isso facilita rodar múltiplas instâncias em paralelo para troubleshooting.

## 🔐 Codecov (opcional)

Se você quiser habilitar upload de cobertura no CI, adicione o secret `CODECOV_TOKEN` em Settings → Secrets → Actions. Com o token presente, o workflow fará upload de cobertura ao final do build.


## 📜 Contrato de erro (resumo)

O formato de erros de execução (quando uma run falha) segue o esqueleto JSON abaixo. Adicione exemplos reais dos logs/artefatos ao documento principal quando houver runs falhas para ajudar debugging.

Exemplo mínimo:

```json
{
	"run_id": "20250929-abcdef",
	"type": "keywords|ads|domains",
	"status": "failed",
	"started_at": "2025-09-29T12:00:00Z",
	"ended_at": "2025-09-29T12:05:05Z",
	"error": {
		"message": "Timeout while fetching search results",
		"step": "fetch_results",
		"stack": "...stack trace or summarized error..."
	},
	"artifacts": {
		"log": "logs/keywords-20250929-abcdef.log",
		"snapshot": "logs/html_failures/20250929-abcdef.html"
	}
}
```

Manter esse padrão facilita triagem automática, agrupamento por erro e upload de pacotes de diagnóstico.
