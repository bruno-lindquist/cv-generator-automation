# CV Generator - Roteiro de Entrevista Técnica

## 1) Pitch de 60–90 segundos (fala)

### Contexto (1–2 frases)
O **CV Generator** é um projeto individual para gerar currículo personalizado em PDF, com suporte a português e inglês, a partir de um único JSON.  
Ele resolve a dor de produzir versões consistentes do CV rapidamente, sem edição manual repetitiva.

### Problema (1–2 frases)
O processo manual de manter currículo atualizado em dois idiomas é lento, sujeito a inconsistências e difícil de padronizar visualmente.  
Além disso, mudanças de conteúdo e layout costumam exigir retrabalho frequente.

### Solução (o que foi construído)
Construí uma automação em linha de comando que lê dados estruturados em JSON, aplica validações, resolve traduções por idioma e renderiza um PDF com layout configurável.  
O fluxo permite escolher idioma, arquivo de entrada, saída e configuração via parâmetros de CLI.

### Minha contribuição (o que eu fiz pessoalmente)
Eu fiz o projeto inteiro de ponta a ponta: arquitetura, implementação da CLI, camada de serviço, renderização PDF, internacionalização, validações, tratamento de erro, logging estruturado, testes e pipelines de CI.

### Decisões e trade-offs (3–5 bullets)
- Separei domínio, serviço e infraestrutura para facilitar manutenção, aceitando um pouco mais de código inicial.
- Mantive JSON como fonte de dados e configuração por ser simples de editar, com trade-off de menor rigidez que um banco/schema formal.
- Usei registry de formatadores por seção para extensibilidade, ao custo de mais objetos para navegar.
- Priorizei robustez com validações e logs detalhados, aceitando mais verbosidade operacional.

### Resultados/impacto (bullets)
- Geração automática de CV bilíngue com consistência de conteúdo e layout.
- Pipeline técnico estável com **38 testes passando** e **90,68% de cobertura** no estado atual.
- CI com lint, testes em matriz de versões Python e auditoria de dependências.
- Como não tenho métricas de negócio consolidadas ainda, eu mediria:
- Tempo médio de geração por CV (p50/p95).
- Taxa de falha por execução (validação, parsing, renderização).
- Tempo de retrabalho manual após geração.
- Volume de CVs gerados por período e lead time total.

### Tecnologias utilizadas (lista agrupada)
**Linguagem e aplicação**
- `Python`: base da automação, regras de negócio e orquestração.
- `argparse` (CLI): entrada parametrizada para idioma, input, output e config.
- `dataclasses`: tipagem e estruturação das configurações da aplicação.

**Dados e internacionalização**
- `JSON`: fonte única de dados do CV, traduções e estilos.
- Mecanismo de i18n próprio (`pt`/`en`): seleção de campos localizados com fallback controlado.

**Geração de documento**
- `ReportLab`: renderização do PDF (estilos, layout, parágrafos, espaçamentos).
- Registry de formatadores: extensibilidade para tipos de seção sem acoplamento no renderer.

**Qualidade e entrega**
- `pytest`: testes unitários e de integração.
- `pytest-cov`: medição de cobertura e gate mínimo.
- `flake8`: lint e padronização de qualidade estática.
- `GitHub Actions`: automação de lint, testes e segurança em push/PR.
- `pip-audit`: verificação de vulnerabilidades de dependências.

**Observabilidade**
- `Loguru`: logs estruturados com eventos, etapas, `request_id` e rotação em arquivo.


### Perguntas inteligentes para o entrevistador (3 perguntas)
1. Nesse time, vocês valorizam mais velocidade de entrega inicial ou observabilidade/robustez desde o começo?
2. Como vocês costumam evoluir contratos de dados sem quebrar compatibilidade com versões anteriores?
3. Qual é o nível esperado de cobertura e qualidade para considerar um projeto pronto para produção?

---

## 2) Versão de 2–3 minutos (fala)

### Contexto (1–2 frases)
O projeto **CV Generator** nasceu para resolver uma dor prática: gerar currículo personalizado de forma rápida em dois idiomas, com padrão visual consistente.  
Foi um projeto **solo**, desenvolvido para transformar um processo manual e repetitivo em um fluxo automatizado e previsível.

### Problema (1–2 frases)
Antes, manter múltiplas versões do CV exigia ajustes manuais frequentes, o que aumentava risco de inconsistência entre idiomas e perda de tempo operacional.

### Solução (o que foi construído)
Implementei uma aplicação CLI em Python com arquitetura em camadas.  
O fluxo é: carregar configuração -> ler JSON de dados/estilos/traduções -> validar payload mínimo -> resolver idioma com fallback -> montar PDF via ReportLab -> salvar arquivo com nome seguro -> registrar logs estruturados.  
O sistema permite customizar input, output, idioma e arquivo de config por parâmetro, além de habilitar/desabilitar seções e ordenar conteúdo via JSON.

### Minha contribuição (o que eu fiz pessoalmente)
Conduzi o projeto de ponta a ponta: desenho da arquitetura, implementação do core de geração, construção do pipeline de renderização por seções, definição do mecanismo de localização, validações de entrada e segurança de caminho de saída, padronização de logs e criação da suíte de testes com CI.  
Como foi um projeto individual, todas as decisões técnicas e trade-offs passaram por mim;

### Decisões e trade-offs (3–5 bullets)
- Arquitetura por responsabilidades (`cli` -> `service` -> `infrastructure`) para reduzir acoplamento; trade-off: mais componentes para manter.
- Configuração e conteúdo fora do código (`config.json`, `styles.json`, `translations.json`) para flexibilidade; trade-off: exige validação rigorosa para evitar erro em runtime.
- Formatação por `SectionFormatterRegistry` para extensibilidade de novas seções; trade-off: aumenta a superfície de testes unitários.
- Fallback de idioma (`pt/en/default`) para robustez de conteúdo; trade-off: pode mascarar ausência de tradução se não houver monitoramento.
- Logging estruturado por evento/etapa para troubleshooting rápido; trade-off: mais cuidado com padronização de campos.

### Resultados/impacto (bullets)
- Entrega de um fluxo reproduzível para gerar CV bilíngue sem edição manual de layout.
- Base técnica coberta por testes automatizados: **38 testes** e **90,68% de cobertura** no estado atual.
- Qualidade contínua automatizada com lint, testes em múltiplas versões de Python e auditoria de dependências.
- Métricas recomendadas para evolução de impacto:
- Tempo total de geração por execução e por etapa (leitura, validação, renderização).
- Taxa de erros por tipo (configuração, dados inválidos, renderização).
- Percentual de execuções sem retrabalho manual.
- Tempo para introduzir nova seção de CV (métrica de extensibilidade).

### Tecnologias utilizadas (lista agrupada)
**Core**
- `Python`: implementação do serviço e regras de negócio.
- `argparse`: interface CLI e contrato de uso do usuário.
- `setuptools` + `pyproject.toml`: empacotamento e comando executável (`cv-generator`).

**Documento e layout**
- `ReportLab`: geração do PDF em A4 com estilos parametrizados.
- Engine de estilos customizada: converte JSON em estilos ReportLab com validação.
- Formatadores por seção (timeline/simple): padroniza renderização e facilita extensão.

**Dados e localização**
- `JSON`: persistência simples para dados, tradução e tema visual.
- Camada de localização customizada: resolução de campos `pt/en` com fallback seguro.

**Qualidade, CI e segurança**
- `pytest`: testes unitários e integração do fluxo completo.
- `pytest-cov`: governança de cobertura mínima.
- `flake8` + `compileall`: qualidade estática e checagem de sintaxe.
- `GitHub Actions`: execução automatizada de lint/test/security em PR e push.
- `pip-audit`: auditoria de vulnerabilidades de bibliotecas.

**Observabilidade**
- `Loguru`: logs estruturados com rotação, retenção e contexto por requisição.


### Perguntas inteligentes para o entrevistador (3 perguntas)
1. Como o time decide quando manter arquitetura simples e quando modularizar mais cedo?
2. Quais sinais vocês usam para priorizar observabilidade em ferramentas internas?
3. Em projetos de automação, quais métricas de impacto vocês consideram mais relevantes para negócio?

---

## 3) Deep dive técnico (5–8 minutos)

### Contexto (1–2 frases)
O **CV Generator** foi concebido como uma automação de geração de currículo em PDF bilíngue para reduzir esforço manual e aumentar consistência entre versões.  
É um projeto individual, com foco em engenharia de software aplicada: arquitetura clara, qualidade automatizada e operação rastreável.

### Problema (1–2 frases)
Gerar e manter CV em dois idiomas manualmente tende a criar inconsistência de conteúdo, quebra de formatação e alta dependência de edição repetitiva.

### Solução (o que foi construído)
Construí uma pipeline CLI orientada a camadas:

1. **Entrada/controle (CLI)**  
Recebe `input`, `language`, `output` e `config`; converte erros de domínio em código de saída controlado.

2. **Orquestração (service)**  
Carrega config tipada, resolve caminhos relativos ao projeto, define idioma efetivo, cria contexto de execução (`request_id`) e coordena o fluxo de ponta a ponta.

3. **Dados e validação**  
Lê JSON de dados/estilos/traduções com tratamento semântico de erros; valida campos obrigatórios do payload antes da renderização.

4. **Renderização PDF (infra)**  
`CvPdfRenderer` monta documento A4; `PdfStyleEngine` valida e materializa estilos; `SectionFormatterRegistry` delega cada seção ao formatter correto (timeline/simple), mantendo extensibilidade.

5. **Saída, deploy e observabilidade**  
Gera arquivo com nome sanitizado e proteção contra escape de diretório; 
logs estruturados em console + arquivo rotativo; 
CI no GitHub Actions executa lint, testes em matriz Python e auditoria de dependências.

### Minha contribuição (o que eu fiz pessoalmente)
Eu implementei todo o ciclo técnico: arquitetura, contratos de entrada, internacionalização com fallback, renderer de PDF por seções, validações, exceções de domínio, segurança de path de saída, logs estruturados, testes unitários e integração, além da esteira de CI com qualidade e segurança.  
Foi um desenvolvimento solo, com duração total não formalmente registrada.

### Decisões e trade-offs (3–5 bullets)
- **Arquitetura modular vs simplicidade imediata**: optei por separar responsabilidades para facilitar evolução; trade-off foi maior esforço inicial.

- **Configuração externa em JSON vs configuração hardcoded**: aumentei flexibilidade de manutenção; trade-off foi necessidade de validações robustas de config/estilo.

- **Fallback de idioma para resiliência vs falha estrita**: priorizei disponibilidade de geração mesmo com lacunas de tradução; risco é esconder dívida de conteúdo, mitigado por logs e revisão.

- **Registry de seção vs if/else centralizado**: escolhi extensibilidade e baixo acoplamento; trade-off é exigir disciplina de testes por formatter.

- **Logging estruturado detalhado vs implementação mínima**: investi em diagnósticos e observabilidade desde cedo; trade-off é overhead de padronização de eventos.

### Resultados/impacto (bullets)
- Processo de geração bilíngue padronizado e reproduzível por comando.
- Qualidade técnica atual validada por **38 testes aprovados** e **90,68% de cobertura**.
- Pipeline de entrega com verificação de estilo, testes multi-versão e auditoria de segurança.
- Como métrica de impacto de produto ainda não foi formalizada, eu mediria:
- Tempo de geração por CV (p50/p95) e tempo por etapa do pipeline.
- Taxa de erro por categoria (dados, config, renderização, I/O).
- Redução de esforço manual (minutos por atualização de CV).
- Frequência de mudanças de conteúdo/layout e taxa de regressão após mudança.

### Tecnologias utilizadas (lista agrupada)
**Arquitetura e aplicação**
- `Python`: implementação principal da aplicação.
- `argparse`: contrato de uso em linha de comando.
- `dataclasses`: modelagem tipada de configuração (`AppConfig`).
- Padrão `Registry`: desacoplamento entre tipo de seção e formatter.

**Renderização e apresentação**
- `ReportLab`: engine de PDF (documento, parágrafos, estilos, espaçamentos).
- Engine de estilos custom (`PdfStyleEngine`): valida e traduz JSON de estilo para objetos ReportLab.

**Dados, i18n e segurança**
- `JSON`: armazenamento de conteúdo, traduções e estilo.
- Módulo de localização custom: resolução `pt/en`, fallback e tratamento de rich text.
- Sanitização de nome de arquivo e validação de caminho: prevenção de path traversal na saída.

**Confiabilidade e operação**
- `Loguru`: logs estruturados por evento/etapa, com rotação e retenção.
- Exceções de domínio (`ConfigurationError`, `DataValidationError`, etc.): falhas semânticas e tratamento previsível.

**Qualidade e entrega contínua**
- `pytest`: suíte unitária e integração.
- `pytest-cov`: cobertura com threshold.
- `flake8`: lint estático.
- `GitHub Actions`: jobs de lint, teste (Python 3.10/3.11/3.12) e segurança.
- `pip-audit`: auditoria de dependências.


### Perguntas inteligentes para o entrevistador (3 perguntas)
1. Como vocês equilibram dívida técnica e velocidade em ferramentas internas com impacto direto no negócio?
2. Qual maturidade de observabilidade vocês esperam para considerar um serviço “operável” em produção?
3. No contexto de vocês, o que pesa mais em avaliação técnica: arquitetura, qualidade de código, ou impacto mensurável de produto?
