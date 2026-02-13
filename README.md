# CV Generator Automation

Gerador automatizado de currículos em PDF a partir de dados JSON, com suporte multilíngue (Português e Inglês). Toda a aparência visual, os textos traduzidos e os dados do candidato são configuráveis por arquivos JSON — sem necessidade de alterar código.

---

## Índice

- [Visão Geral](#visão-geral)
- [Mapa Estrutural do Projeto](#mapa-estrutural-do-projeto)
- [Arquitetura e Fluxo de Execução](#arquitetura-e-fluxo-de-execução)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
  - [Geração rápida (script automático)](#geração-rápida-script-automático)
  - [CLI manual](#cli-manual)
  - [Exemplos de uso](#exemplos-de-uso)
- [Configuração](#configuração)
  - [config.json — Configuração da aplicação](#configjson--configuração-da-aplicação)
  - [cv_data.json — Dados do currículo](#cv_datajson--dados-do-currículo)
  - [styles.json — Aparência visual do PDF](#stylesjson--aparência-visual-do-pdf)
  - [translations.json — Traduções de seções e rótulos](#translationsjson--traduções-de-seções-e-rótulos)
- [Seções suportadas](#seções-suportadas)
- [Localização e Fallback de idioma](#localização-e-fallback-de-idioma)
- [Logging e Observabilidade](#logging-e-observabilidade)
- [Testes](#testes)
- [Scripts Auxiliares](#scripts-auxiliares)
- [Stack Tecnológica](#stack-tecnológica)

---

## Visão Geral

O projeto recebe um JSON com os dados profissionais do candidato e produz um PDF formatado pronto para envio. O pipeline completo executa:

1. Carregamento e validação de configuração
2. Leitura dos dados do currículo (com resolução automática por idioma)
3. Validação de campos obrigatórios
4. Renderização de cada seção em PDF via ReportLab
5. Gravação do arquivo final com nome derivado do candidato

Cada etapa é instrumentada com logs estruturados contendo `request_id`, idioma e duração.

---

## Mapa Estrutural do Projeto

```
cv-generator-automation/
│
├── config/                          # Configurações da aplicação
│   ├── config.json                  # Caminhos de arquivos, idioma padrão, logging
│   ├── styles.json                  # Margens, espaçamentos, cores e estilos de parágrafo
│   └── translations.json            # Traduções dos títulos de seção e rótulos
│
├── data/                            # Dados de entrada
│   ├── cv_data.json                 # Dados reais do currículo (editável)
│   └── cv_data_example.json         # Exemplo de referência com todas as seções
│
├── src/                             # Código-fonte principal
│   ├── cli.py                       # Entrada de linha de comando (argparse)
│   ├── cv_service.py                # Caso de uso: orquestra todo o pipeline de geração
│   ├── exceptions.py                # Hierarquia de exceções de domínio
│   ├── localization.py              # Tradução, fallback de idioma, escape XML, formatação
│   ├── logging_config.py            # Configuração de logging estruturado (Loguru)
│   ├── validators.py                # Validação de campos obrigatórios do payload
│   │
│   └── infrastructure/              # Camada de infraestrutura (I/O, renderização)
│       ├── config_loader.py         # Leitura e parsing tipado do config.json
│       ├── json_repository.py       # Carregamento genérico de JSON com erros de domínio
│       │
│       ├── pdf_renderer.py          # Renderizador principal — monta documento ReportLab
│       │
│       ├── pdf_sections/            # Formatadores de seção do PDF
│       │   ├── base.py              # Classe abstrata + helpers compartilhados
│       │   ├── registry.py          # Registry: mapeia tipo de seção → formatador
│       │   ├── simple.py            # Seções diretas: skills, languages, awards, certs
│       │   └── timeline.py          # Seções cronológicas: experience, education
│       │
│       └── pdf_styles/              # Motor de estilos visuais
│           └── pdf_style_engine.py  # Converte styles.json → ParagraphStyles ReportLab
│
├── tests/                           # Suite de testes (pytest)
│   ├── conftest.py                  # Fixtures globais
│   ├── helpers/                     # Builders e utilities para testes
│   │   ├── file_helpers.py          # Gravação de JSON temporário
│   │   ├── project_builders.py      # Fábricas de estrutura de projeto para testes
│   │   └── style_helpers.py         # Carregamento do styles.json real
│   ├── unit/                        # Testes unitários por módulo
│   │   ├── test_cli.py
│   │   ├── test_cv_service_language_paths.py
│   │   ├── test_localization.py
│   │   ├── test_pdf_renderer_sections.py
│   │   ├── test_pdf_section_formatters.py
│   │   ├── test_pdf_style_engine.py
│   │   ├── test_section_formatter_registry.py
│   │   └── test_validators.py
│   └── integration/                 # Teste de integração (pipeline completo)
│       └── test_cv_generation_service.py
│
├── output/                          # PDFs gerados (criado automaticamente)
├── logs/                            # Logs da aplicação (criado automaticamente)
│
├── pyproject.toml                   # Definição do projeto, dependências e scripts
├── start_mac.sh                     # Gera CV em PT e EN automaticamente
└── clean_project.command            # Remove artefatos temporários do projeto
```

---

## Arquitetura e Fluxo de Execução

```
┌─────────┐     ┌──────────────────────┐     ┌──────────────┐
│  CLI    │────▶│  CvGenerationService │────▶│  Validators  │
│         │     │    cv_service.py     │     │              │
└─────────┘     └──────────┬───────────┘     └──────────────┘
                           │
              ┌────────────┼────────────────┐
              ▼            ▼                ▼
     ┌──────────────┐ ┌──────────┐  ┌─────────────┐
     │config_loader │ │json_repo │  │localization │
     └──────────────┘ └──────────┘  └─────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ pdf_renderer.py │
                  └────────┬────────┘
                           │
              ┌────────────┼──────────────┐
              ▼            ▼              ▼
     ┌───────────────┐ ┌──────────┐ ┌─────────────────┐
     │ pdf_style_eng │ │ registry │ │ simple/timeline │
     └───────────────┘ └──────────┘ └─────────────────┘
                           │
                           ▼
                      [ output.pdf ]
```

**Responsabilidades por camada:**

| Camada | Arquivos | Papel |
|--------|----------|-------|
| **Entrada** | `cli.py` | Parseia argumentos, invoca o serviço, trata erros como código de saída |
| **Domínio** | `cv_service.py`, `validators.py`, `exceptions.py` | Orquestra pipeline, valida dados, define erros tipados |
| **Localização** | `localization.py` | Resolve campos por idioma com cadeia de fallback, escapa XML, formata datas |
| **Infraestrutura** | `config_loader.py`, `json_repository.py` | Lê e valida JSON, devolve estruturas tipadas imutáveis |
| **Renderização** | `pdf_renderer.py`, `pdf_sections/*`, `pdf_styles/*` | Converte dados em elementos ReportLab e grava PDF |
| **Observabilidade** | `logging_config.py` | Logging estruturado com Loguru (arquivo + console, rotação, retenção) |

---

## Pré-requisitos

- **Python 3.10+**
- **pip** (incluído no Python)

---

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd cv-generator-automation
```

### 2. Crie e ative um ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Instale o projeto

```bash
pip install -e .
```

Isso instala as dependências (`reportlab`, `loguru`) e registra o comando `cv-generator`.

### 4. (Opcional) Instale dependências de desenvolvimento

```bash
pip install -e ".[dev]"
```

Inclui `pytest`, `pytest-cov`, `flake8` e `pip-audit`.

---

## Uso

### Geração rápida (script automático)

O script `start_mac.sh` gera automaticamente o CV em Português e Inglês:

```bash
chmod +x start_mac.sh
./start_mac.sh
```

Os PDFs são salvos em `output/`.

### CLI manual

```bash
cv-generator [INPUT] [-l IDIOMA] [-o SAÍDA] [-c CONFIG]
```

| Argumento | Descrição |
|-----------|-----------|
| `INPUT` (posicional, opcional) | Caminho para arquivo JSON com dados do CV. Se omitido, usa o definido em `config.json` |
| `-l`, `--language` | Idioma: `pt` (Português) ou `en` (Inglês). Padrão definido em `config.json` |
| `-o`, `--output` | Caminho do PDF de saída. Se omitido, nome é gerado automaticamente |
| `-c`, `--config` | Caminho do arquivo de configuração. Padrão: `config/config.json` |

### Exemplos de uso

```bash
# Gerar CV em português (padrão)
cv-generator

# Gerar CV em inglês
cv-generator -l en

# Usar arquivo de dados específico
cv-generator data/cv_data_example.json -l en

# Definir nome do arquivo de saída
cv-generator -l pt -o meu_curriculo.pdf

# Executar sem instalar (via módulo)
PYTHONPATH=src python -m cli -l pt
```

---

## Configuração

### config.json — Configuração da aplicação

Localizado em `config/config.json`. Define caminhos (relativos ao diretório do config), idioma padrão e logging.

```json
{
  "files": {
    "data": "../data/cv_data.json",
    "styles": "styles.json",
    "translations": "translations.json",
    "output_dir": "../output"
  },
  "defaults": {
    "language": "pt",
    "encoding": "utf-8"
  },
  "logging": {
    "enabled": true,
    "level": "info",
    "directory": "../logs"
  }
}
```

**Suporte a mapeamento por idioma** — para usar arquivos de dados ou traduções diferentes por idioma, substitua o caminho único por um mapeamento:

```json
{
  "files": {
    "data_by_language": {
      "pt": "../data/cv_data_pt.json",
      "en": "../data/cv_data_en.json"
    }
  }
}
```

### cv_data.json — Dados do currículo

Localizado em `data/`. Contém informações pessoais, cargo desejado, resumo e todas as seções. Campos textuais suportam localização automática:

**Campos obrigatórios:** `personal_info` (com `name` e `email`) e `desired_role`.

**Controle de seções:** o array `sections` define quais seções aparecem no PDF, a ordem (`order`) e se estão habilitadas (`enabled`). Seções com `"enabled": false` são omitidas.

**Formatação rica:** campos de texto suportam tags `<b>`, `<i>` e `<u>` para negrito, itálico e sublinhado.

### styles.json — Aparência visual do PDF

Localizado em `config/`. Controla margens, espaçamentos, cores e estilos tipográficos sem alterar código.

| Seção | Controla |
|-------|----------|
| `margins` | Margens da página (mm): `top`, `bottom`, `left`, `right` |
| `spacing` | Espaçamento entre blocos: `header_bottom`, `section_bottom`, `item_bottom`, etc. |
| `links` | Cor dos links sociais no cabeçalho (`social_link_color`) |
| `paragraph_styles` | Estilo de cada elemento: fonte, tamanho, cor, alinhamento, indentação |

Estilos de parágrafo obrigatórios: `NameStyle`, `TitleStyle`, `SectionTitleStyle`, `ItemTitleStyle`, `ItemSubtitleStyle`, `BodyStyle`, `ContactStyle`, `DateStyle`.

### translations.json — Traduções de seções e rótulos

Localizado em `config/`. Mapeia nomes de seções e rótulos para cada idioma.

## Seções suportadas

| Tipo (`type`) | Formatador | Campos principais |
|---------------|-----------|-------------------|
| `experience` | Timeline | `position`, `company`, `start_month/year`, `end_month/year`, `description` |
| `education` | Timeline | `degree`, `institution`, `start_month/year`, `end_month/year`, `description` |
| `core_skills` | Simple | `category`, `description` (lista com bullets) |
| `skills` | Simple | `category`, `item` (lista separada por vírgulas) |
| `languages` | Simple | `language`, `proficiency` |
| `certifications` | Simple | `name`, `issuer`, `year` |
| `awards` | Simple | `title`, `description` |

Todos os campos textuais aceitam localização por idioma (`{"pt": "...", "en": "..."}`).

---

**Cadeia de fallback:** idioma solicitado → `pt` → `en` → `default` → primeiro valor disponível.

---

## Logging e Observabilidade

O sistema usa **Loguru** com logs estruturados contendo:

- `request_id` — identificador único da geração
- `language` — idioma ativo
- `step` — etapa do pipeline (`cli`, `validators`, `pdf_renderer`, etc.)
- `event` — tipo de evento (`app_start`, `section_render_finished`, etc.)
- `duration_ms` — duração de etapas críticas

Logs são gravados em `logs/cv_generator.log` (rotação a cada 5 MB, retenção de 14 dias) e exibidos no console. O logging pode ser desabilitado em `config.json` (`"enabled": false`).

---

## Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=term-missing

# Apenas testes unitários
pytest tests/unit/

# Apenas teste de integração
pytest tests/integration/
```

**Organização dos testes:**

| Diretório | Escopo |
|-----------|--------|
| `tests/unit/` | Testes isolados por módulo (CLI, validadores, localization, style engine, formatadores, registry) |
| `tests/integration/` | Pipeline completo: config → dados → validação → PDF |
| `tests/helpers/` | Builders de projeto temporário e utilidades de fixture |

Os testes de integração criam projetos temporários completos em `tmp_path` e validam a geração real de PDFs.

---

## Scripts Auxiliares

| Script | Função |
|--------|--------|
| `start_mac.sh` | Gera CV em PT e EN automaticamente (detecta venv e SO) |
| `clean_project.command` | Remove `output/`, `logs/`, `__pycache__/`, `.egg-info`, `.pyc` e artefatos de build. Preserva `.venv/` e `.git/` |

---

## Stack Tecnológica

| Componente | Tecnologia |
|------------|------------|
| Linguagem | Python 3.10+ |
| Geração de PDF | ReportLab 4.0.9 |
| Logging | Loguru 0.7.2 |
| Testes | pytest 8.3, pytest-cov 6.0 |
| Linting | flake8 7.1 |
| Auditoria | pip-audit 2.7 |
| Gerenciamento | pyproject.toml (setuptools) |
