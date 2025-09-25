PR title:
feat(mockadapter): populate domain field for mocked ads

Description:
### O que foi feito
- MockAdapter agora popula o campo `domain` em anúncios mockados no formato {keyword}.example.com.
- Adicionado teste unitário (tests/test_mock_adapter.py) garantindo que anúncios mockados sempre têm domain não-nulo.

### Impacto
- Endpoint /domains retorna dados úteis em vez de null.
- Aba Métricas mostra breakdown mais informativo.
- Contrato selado por teste unitário.

### Como testar
1. Rodar `python scripts/run_demo.py` ou iniciar um Mock Run pela GUI.
2. Consultar /domains → deve listar domínios preenchidos.
3. Consultar /metrics → per_keyword inclui ads com domain.
4. Rodar `pytest tests/test_mock_adapter.py` → deve passar.

### Próximos passos sugeridos
- Refinar UX da aba Métricas (formatos numéricos, spinner/feedback).
- Expandir MockAdapter para usar uma lista variada de domínios (opcional).
