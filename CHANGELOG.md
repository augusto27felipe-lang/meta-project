# Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.

O formato segue as convenções do [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [v3.1] - 2025-09-25
### Added
- **MockAdapter**: agora popula o campo `domain` para cada anúncio, permitindo relatórios e métricas por domínio.
- **GUI**: aba *Métricas* com spinner de carregamento e formatação numérica; aba *Anúncios* implementada para listar anúncios via API.
- **Backend (FastAPI)**: novos endpoints `/ads`, `/runs`, `/domains`, `/metrics` com cálculo de percentis (p50, p95) e breakdown por keyword.
- **Persistência**: entidades `KeywordRun` e `Ad` persistidas via SQLAlchemy.
- **Testes**: novos testes de integração e unitários para MockAdapter e endpoints.

### Notes
- Recomenda-se validar o patch em um clone de teste antes de aplicar em produção.
- O patch consolidado (`v3.1.patch`) está disponível na release.

---

## [Unreleased]
- Planejamento para futuras melhorias e novas features.
