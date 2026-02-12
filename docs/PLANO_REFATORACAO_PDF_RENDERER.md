# Plano de Execução - Refatoração do `pdf_renderer.py` (Opções 2 + 3)

## Objetivo
Reduzir a complexidade do arquivo `/Users/bruno/Downloads/cv_editavel3/cv-generator-automation/src/infrastructure/pdf_renderer.py` separando:
1. Engine de estilos (opção 3).
2. Formatadores de seções por módulo (opção 2).

Sem alterar o comportamento funcional de geração do PDF.

## Princípios obrigatórios durante execução
- DRY obrigatório em todo código novo e toda refatoração.
- Nomes autoexplicativos para pastas, arquivos, classes, funções e variáveis.
- Cada fase deve preservar compatibilidade funcional.
- Cada fase só fecha com validação executada e resultado registrado.

## Estrutura alvo (referência)
```text
src/
  infrastructure/
    pdf_renderer.py                  # Orquestrador (arquivo menor)
    pdf_styles/
      style_config_validator.py
      paragraph_style_factory.py
      style_values_resolver.py
    pdf_sections/
      base_section_formatter.py
      section_formatter_registry.py
      experience_section_formatter.py
      education_section_formatter.py
      core_skills_section_formatter.py
      skills_section_formatter.py
      languages_section_formatter.py
      awards_section_formatter.py
      certifications_section_formatter.py
```

---

## Fase 1 - Baseline e contrato de comportamento
### Descritivo detalhado
Nesta fase será definido o comportamento atual como contrato para evitar regressão durante a refatoração.
Serão mapeados os pontos críticos do renderer atual: ordem de seções, tratamento de seções inválidas, regras de espaçamento, estilos e tratamento de erros.
Também serão definidos critérios de equivalência funcional entre antes/depois da refatoração.

### Checklist
- [x] Mapear todos os métodos atuais de `pdf_renderer.py` e classificar por responsabilidade.
- [x] Registrar quais métodos pertencem a: estilo, orquestração, ou formatação de seção.
- [x] Definir lista de cenários obrigatórios de regressão (PT, EN, saída padrão, saída customizada).
- [x] Definir critérios de equivalência do PDF (arquivo gerado, tamanho mínimo, nome esperado).
- [x] Congelar baseline de testes antes de qualquer extração estrutural.

### Validação da fase
- [x] Executar `./.venv/bin/pytest -q`.
- [x] Executar geração real: `./.venv/bin/python cv_generator.py -l pt -o output/_baseline_pt.pdf`.
- [x] Executar geração real: `./.venv/bin/python cv_generator.py -l en -o output/_baseline_en.pdf`.
- [x] Confirmar que todos os comandos acima finalizam com sucesso.

### Critério de pronto
Baseline técnico documentado e comportamento atual claramente definido para comparação nas próximas fases.

---

## Fase 2 - Extração da engine de estilos (opção 3)
### Descritivo detalhado
Nesta fase será removida do renderer toda lógica de parsing, validação e conversão de estilos.
Serão criados componentes dedicados para:
1. Validar estrutura obrigatória do `styles.json`.
2. Converter configurações para objetos `ParagraphStyle`.
3. Resolver valores visuais reutilizáveis (margens, espaçamentos, cor de links).

O `pdf_renderer.py` deve parar de conhecer detalhes internos de schema de estilos.

### Checklist
- [x] Criar módulo `pdf_styles/style_config_validator.py` para validações obrigatórias.
- [x] Criar módulo `pdf_styles/paragraph_style_factory.py` para montagem do `StyleSheet1`.
- [x] Criar módulo `pdf_styles/style_values_resolver.py` para margens, espaçamentos e link color.
- [x] Centralizar mensagens de erro de estilo com exceções claras e autoexplicativas.
- [x] Garantir ausência de duplicação na validação de chaves de estilo.
- [x] Garantir nomes de funções e classes orientados a domínio de estilo.

### Validação da fase
- [x] Criar/ajustar testes unitários para validar erro em chave obrigatória ausente.
- [x] Criar/ajustar testes unitários para validar conversão de alinhamento/cor.
- [x] Executar `./.venv/bin/pytest -q tests/unit`.
- [x] Confirmar que todas as validações de estilo passam sem alterar comportamento externo.

### Critério de pronto
Engine de estilos isolada em módulos próprios e testada, com `pdf_renderer.py` sem regras de parsing/validação de estilo embutidas.

---

## Fase 3 - Adaptação do `pdf_renderer.py` para usar a engine de estilos
### Descritivo detalhado
Nesta fase o arquivo principal será transformado em orquestrador de alto nível.
Ele deve consumir componentes da Fase 2 por composição, mantendo foco em fluxo de renderização.
Qualquer regra visual deve ser lida por interfaces da engine, não por acesso direto ao dicionário bruto.

### Checklist
- [x] Remover do `pdf_renderer.py` métodos de baixo nível relacionados a estilo.
- [x] Injetar/adotar resolvedores de estilo no construtor do renderer.
- [x] Substituir acesso direto ao JSON de estilos por chamadas semânticas.
- [x] Manter mensagens de log e eventos existentes no fluxo principal.
- [x] Revisar nomes para garantir clareza de responsabilidades.

### Validação da fase
- [x] Executar `./.venv/bin/flake8 src tests cv_generator.py`.
- [x] Executar `./.venv/bin/pytest -q`.
- [x] Gerar PDF PT e EN para validar saída após mudança estrutural.
- [x] Confirmar que não houve regressão funcional.

### Critério de pronto
`pdf_renderer.py` reduzido e focado em orquestração, com estilo totalmente delegado à engine extraída.

---

## Fase 4 - Extração dos formatadores de seção (opção 2)
### Descritivo detalhado
Nesta fase cada tipo de seção será movido para seu próprio formatter, com contrato comum.
A intenção é remover do renderer os blocos extensos de formatação específica e reduzir acoplamento.
Será criada uma base reutilizável para evitar repetição entre formatadores (DRY).

### Checklist
- [x] Criar contrato comum em `pdf_sections/base_section_formatter.py`.
- [x] Criar um formatter por seção com nomes explícitos.
- [x] Extrair lógica de cada método `_format_*` para seu respectivo módulo.
- [x] Criar utilitários compartilhados para trechos repetidos (título, período, bullets, escape).
- [x] Garantir que cada formatter tenha responsabilidade única.
- [x] Evitar duplicação de tratamento de texto entre formatadores.

### Validação da fase
- [x] Criar/ajustar testes unitários por formatter.
- [x] Executar `./.venv/bin/pytest -q tests/unit`.
- [x] Validar que cada seção é renderizada corretamente em cenário controlado.
- [x] Confirmar que não há regressão em conteúdo textual do PDF.

### Critério de pronto
Formatadores de seções totalmente isolados por módulo, com contrato comum e cobertura unitária adequada.

---

## Fase 5 - Registry de formatadores + integração no renderer
### Descritivo detalhado
Nesta fase será criado um registry para mapear `section_type` para formatter, removendo `if/else` e mapeamentos dispersos.
O renderer passa a iterar seções e delegar ao registry.
Com isso, inclusão de nova seção passa a exigir apenas novo formatter + registro explícito.

### Checklist
- [x] Criar `pdf_sections/section_formatter_registry.py`.
- [x] Registrar formatadores padrão do projeto em ponto único.
- [x] Delegar renderização de seção ao formatter resolvido pelo registry.
- [x] Manter tratamento de seções desconhecidas com `WARNING`.
- [x] Garantir que ordem definida em `sections` continue respeitada.

### Validação da fase
- [x] Testar seção desconhecida e confirmar log `WARNING`.
- [x] Testar ordem de seções configurada no JSON de entrada.
- [x] Executar `./.venv/bin/pytest -q tests/integration`.
- [x] Confirmar geração de PDF com múltiplas seções.

### Critério de pronto
Orquestração de seções desacoplada, extensível e com ponto único de registro.

---

## Fase 6 - Limpeza final, documentação e hardening
### Descritivo detalhado
Nesta fase serão removidos restos da implementação antiga, consolidando nomenclatura, imports e documentação.
Também serão adicionadas instruções para manutenção futura, incluindo como criar novos estilos e novas seções sem quebrar DRY.

### Checklist
- [x] Remover código morto e imports não utilizados.
- [x] Garantir que não exista duplicação entre renderer e formatadores.
- [x] Atualizar README e docs com nova arquitetura do pipeline de PDF.
- [x] Documentar procedimento para adicionar uma nova seção.
- [x] Documentar procedimento para alterar estilos via `config/styles.json`.
- [x] Revisar nomes de arquivos/classes para máxima clareza semântica.

### Validação da fase
- [x] Executar `./.venv/bin/flake8 src tests cv_generator.py`.
- [x] Executar `./.venv/bin/pytest -q`.
- [x] Executar geração real PT/EN e validar arquivos de saída.
- [x] Revisão final de diff para confirmar foco apenas na refatoração planejada.

### Critério de pronto
Refatoração concluída com renderer enxuto, estilo desacoplado, seções modularizadas, documentação atualizada e validação completa.

---

## Critério global de sucesso
- [x] `pdf_renderer.py` com responsabilidade estritamente de orquestração.
- [x] Estilos 100% centralizados no fluxo de `config/styles.json` via engine dedicada.
- [x] Seções 100% modularizadas em formatadores independentes.
- [x] Código DRY e nomenclatura autoexplicativa em todos os novos módulos.
- [x] Suíte de testes e execução real sem regressão funcional.
