PR title (sugestão)
feat(gui+api+tests): add Metrics tab, expose per_keyword in /metrics, add integration tests

PR description (sugestão — cole este bloco primeiro)
Adiciona aba "Anúncios" e aba "Métricas" na GUI (consomem /ads e /metrics).
Expande API: /ads, /runs, /domains, /metrics com breakdown por keyword (per_keyword).
Adiciona testes de integração test_api_integration.py usando FastAPI TestClient; o banco é recriado por teste para garantir isolamento.
Pequenas correções e robustez: unique_id requerido respeitado nos seeds/tests; GUI trata erros de fetch e colore job.error em vermelho.

### Como testar localmente
python scripts/seed.py
python scripts/run_demo.py (ou abrir GUI e clicar Start Mock Run)
uvicorn backend.etapa4_service.main:app --reload
Abrir as abas Anúncios/Métricas na GUI e clicar “Atualizar”.

### Sugestões futuras (não incluídas neste PR)
- Fazer MockAdapter popular domain para tornar /domains mais útil.
- Melhorar UX da aba Métricas (formatos, spinner).
- Adicionar Alembic migrations.
- Criar teste E2E que executa JobManager + MockAdapter e valida endpoints via TestClient.


Checklist de PR — V3.1 (cole este bloco após a descrição)
### Implementações
- [x] GUI: adicionadas abas Anúncios e Métricas
- [x] API: endpoints /ads, /runs, /domains e /metrics (com per_keyword)
- [x] Testes de integração: test_api_integration.py com FastAPI TestClient
- [x] Validação manual: scripts/seed.py + scripts/run_demo.py + GUI + curl → endpoints respondem corretamente
- [x] CI local: testes passam localmente (pytest verde)

### Revisão
- [ ] Código compila sem warnings/erros
- [ ] Testes passam no CI
- [ ] GUI exibe anúncios e métricas corretamente
- [ ] Endpoints retornam JSON esperado
- [ ] Documentação mínima no PR descreve como testar localmente

### Sugestões futuras (não incluídas neste PR)
- [ ] MockAdapter popular domain para enriquecer /domains
- [ ] Melhorar UX da aba Métricas (formatos numéricos, spinner/feedback)
- [ ] Adicionar Alembic migrations
- [ ] Criar teste E2E que roda JobManager + MockAdapter e valida endpoints via TestClient
