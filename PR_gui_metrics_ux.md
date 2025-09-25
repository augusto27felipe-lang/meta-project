PR title:
feat(gui): improve Metrics tab UX with loading indicator and number formatting

Description:
### O que foi feito
- Ao clicar em Atualizar na aba Métricas, a área mostra "Carregando..." e o botão é desabilitado enquanto a requisição ocorre.
- Números agregados e por keyword são formatados com até duas casas decimais para melhor leitura.

### Impacto
- Experiência do usuário mais clara: feedback de carregamento e números legíveis.

### Como testar
1. Rodar a API `uvicorn backend.etapa4_service.main:app --reload`.
2. Abrir a GUI e navegar até a aba Métricas.
3. Clicar em Atualizar e observar "Carregando..." seguido dos dados formatados.

### Próximos passos
- Substituir "Carregando..." por um `ttk.Progressbar` em modo indeterminado para um visual mais moderno.
