# CV Generator - Gerador Automático de Currículos em PDF

Gera currículos profissionais em PDF a partir de JSON, com suporte a português e inglês.

## Visão geral

O projeto foi reorganizado em camadas para manter responsabilidades claras:

- `application`: orquestração do caso de uso de geração.
- `domain`: regras de validação, localização e formatação.
- `infrastructure`: leitura de arquivos, carregamento de config e renderização de PDF.
- `shared`: exceções e configuração de logging.

## Estrutura atual

```text
cv-generator-automation/
  src/
    cv_generator_app/
      application/
      domain/
      infrastructure/
      shared/
      cli.py
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
  cv_generator.py
  requirements.txt
  requirements-dev.txt
  start_mac.sh
```

## Requisitos

- Python 3.10+

## Instalação

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

## Como executar

### Comando principal (compatível com versões anteriores)

```bash
python cv_generator.py
```

### Opções

```bash
python cv_generator.py -l en
python cv_generator.py -o output/meu_cv.pdf
python cv_generator.py -c config/config.json
python cv_generator.py data/cv_data.json -l pt
```

Argumentos:

- `input`: arquivo JSON de entrada (opcional).
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

## Testes

Executar testes com cobertura:

```bash
pytest --cov=src/cv_generator_app --cov-report=term-missing --cov-fail-under=70
```

## CI

Workflows configurados:

- `lint.yml`: flake8 + verificação de sintaxe.
- `test.yml`: testes (matriz Python) + auditoria de dependências com `pip-audit`.
