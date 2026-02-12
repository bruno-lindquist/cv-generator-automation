# Guia de Manutenção do Pipeline PDF

## Visão da arquitetura

O pipeline de renderização é dividido em componentes independentes:

1. `CvPdfRenderer` (`src/infrastructure/pdf_renderer.py`)
- Resolve a ordem das seções.
- Monta cabeçalho, resumo e fluxo de renderização.
- Delega formatação de seção para o registry.

2. `PdfStyleEngine` (`src/infrastructure/pdf_styles/pdf_style_engine.py`)
- Valida o schema de `config/styles.json`.
- Constrói `StyleSheet1` do ReportLab.
- Resolve valores semânticos de margem, espaçamento e cor.

3. `SectionFormatterRegistry` (`src/infrastructure/pdf_sections/section_formatter_registry.py`)
- Centraliza o mapeamento `section_type -> formatter`.
- Mantém ponto único para extensão de novas seções.

4. `BaseSectionFormatter` + formatters específicos (`src/infrastructure/pdf_sections/`)
- Implementam a renderização de cada item de seção.
- Reutilizam helpers comuns para manter DRY.

## Procedimento: adicionar uma nova seção

Checklist executável:

- [ ] Criar formatter dedicado em `src/infrastructure/pdf_sections/<nova_secao>_section_formatter.py`.
- [ ] Herdar de `BaseSectionFormatter` e implementar `format_section_item(...)`.
- [ ] Reutilizar helpers do `BaseSectionFormatter` (evitar duplicação de escape, bullets e espaçamento).
- [ ] Registrar o formatter em `build_default_section_formatter_registry(...)`.
- [ ] Exportar o formatter em `src/infrastructure/pdf_sections/__init__.py` (se necessário).
- [ ] Adicionar tradução do título em `config/translations.json` na chave `sections`.
- [ ] Atualizar JSON de dados (`data/cv_data.json` e `data/cv_data_example.json`) com `type` correspondente.
- [ ] Criar/atualizar testes unitários da nova seção.
- [ ] Executar validação final:
  - `./.venv/bin/flake8 src tests cv_generator.py`
  - `./.venv/bin/pytest -q`
  - `./.venv/bin/python cv_generator.py -l pt -o output/_manual_pt.pdf`
  - `./.venv/bin/python cv_generator.py -l en -o output/_manual_en.pdf`

Critério de pronto:
- Nova seção renderiza sem alterar comportamento das seções existentes.
- Não há duplicação de lógica já presente em outros formatadores.

## Procedimento: alterar estilos via `config/styles.json`

Checklist executável:

- [ ] Ajustar apenas chaves semânticas existentes em `layout`, `spacing` e `paragraph_styles` quando possível.
- [ ] Se adicionar novo `paragraph_style`, atualizar validação caso a chave passe a ser obrigatória.
- [ ] Validar compatibilidade de cor/alinhamento/fonte com o `ParagraphStyleFactory`.
- [ ] Conferir impacto em `PdfStyleEngine` (`margin`, `spacing`, `social_link_color`).
- [ ] Executar testes:
  - `./.venv/bin/pytest -q tests/unit/test_pdf_style_engine.py`
  - `./.venv/bin/pytest -q`
- [ ] Gerar PDF PT/EN e inspecionar visualmente.

Critério de pronto:
- Configuração validada sem erro.
- PDF gerado com espaçamento e tipografia esperados.

## Regras de manutenção (DRY + clareza)

- Todo código novo deve reutilizar utilitários existentes antes de criar novo helper.
- Nomes de arquivos, classes e variáveis devem ser autoexplicativos e orientados ao domínio.
- `CvPdfRenderer` deve permanecer como orquestrador; detalhes de estilo/seção ficam fora dele.
