# CV Generator - Gerador Automático de Currículos em PDF

Gera currículos profissionais em PDF a partir de JSON, com suporte a português e inglês.

## Visão geral

O projeto está organizado com fluxo direto:

- `src/cli.py`: entrypoint de linha de comando.
- `src/cv_service.py`: orquestração do caso de uso de geração.
- `src/localization.py` e `src/validators.py`: regras de domínio.
- `src/infrastructure/`: I/O, configuração e renderização de PDF.
- `src/exceptions.py` e `src/logging_config.py`: base compartilhada da aplicação.

## Estrutura atual

```text
cv-generator-automation/
  src/
    cli.py
    cv_service.py
    localization.py
    validators.py
    exceptions.py
    logging_config.py
    infrastructure/
      config_loader.py
      json_repository.py
      pdf_renderer.py
      pdf_styles/
        pdf_style_engine.py
      pdf_sections/
        base.py
        timeline.py
        simple.py
        registry.py
  tests/
    unit/
    integration/
  data/
    cv_data.json
    cv_data_example.json
  config/
    config.json
    styles.json
    translations.json
  .github/workflows/
  pyproject.toml
  start_mac.sh
```

## Requisitos

- Python 3.10+

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Padrão do projeto:
- use `.venv/` como ambiente virtual local.
- fonte única de dependências: `pyproject.toml`.

## Como executar

### Entry point oficial

```bash
cv-generator
```

### Opções

```bash
cv-generator -l en
cv-generator -o output/meu_cv.pdf
cv-generator -c config/config.json
cv-generator data/cv_data.json -l pt
```

Argumentos:

- `input`: arquivo JSON de entrada (opcional). Padrão: `data/cv_data.json` (definido em `config/config.json`).
- `-l, --language`: idioma (`pt` ou `en`).
- `-o, --output`: caminho do PDF de saída.
- `-c, --config`: arquivo de configuração.

Observação de manutenção:
- Dados e traduções ficam em arquivo único, com conteúdo bilíngue organizado por chave.
- Para campos traduzíveis, use estrutura `{ \"pt\": \"...\", \"en\": \"...\" }`.
- Para listas traduzíveis, use `{ \"pt\": [ ... ], \"en\": [ ... ] }`.
- O idioma informado em `-l` escolhe automaticamente a variante correta no mesmo arquivo.

### Atalho macOS/Linux

```bash
./start_mac.sh
```

## Logging (Loguru)

O sistema utiliza Loguru com:

- sink de console para execução local.
- sink de arquivo rotativo em `logs/cv_generator.log`.
- eventos estruturados (`app_start`, `input_validated`, `section_render_started`, `pdf_build_finished`, etc).

Níveis aplicados:

- `DEBUG`: detalhes de diagnóstico interno.
- `INFO`: progresso normal da geração.
- `WARNING`: anomalias recuperáveis.
- `ERROR`: falhas da operação atual.
- `CRITICAL`: falhas fatais e inesperadas.

## Arquitetura do pipeline PDF

O fluxo de geração de PDF está separado por responsabilidade:

- `CvPdfRenderer` (`src/infrastructure/pdf_renderer.py`): orquestra o fluxo de renderização.
- `PdfStyleEngine` (`src/infrastructure/pdf_styles/pdf_style_engine.py`): valida e resolve estilos a partir de `config/styles.json`.
- `SectionFormatterRegistry` (`src/infrastructure/pdf_sections/registry.py`): mapeia cada `section_type` para um formatter.
- `BaseSectionFormatter` e especializações (`src/infrastructure/pdf_sections/base.py`, `src/infrastructure/pdf_sections/timeline.py`, `src/infrastructure/pdf_sections/simple.py`).

Referência operacional:
- esta seção do `README.md` é a fonte de verdade para manutenção do pipeline PDF.

## Testes

Fluxo de teste único:

```bash
pytest -q
```

Cobertura:

```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=70
```

## CI

Workflows configurados:

- `lint.yml`: flake8 + verificação de sintaxe.
- `test.yml`: testes (matriz Python) + auditoria de dependências com `pip-audit`.
