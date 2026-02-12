# Plano de Execução Técnico - CV Generator

## Objetivo
Executar uma evolução completa do projeto com foco em arquitetura modular, qualidade, observabilidade e testes, sem alterar o escopo funcional principal de geração de CV em PDF.

## Escopo deste plano
- Inclui refatoração arquitetural, melhoria de qualidade, testes e CI.
- Inclui implantação de logging estruturado com Loguru.
- Não prioriza ações de anonimização de dados pessoais, conforme solicitado.

## Regras obrigatórias de execução (sempre)
1. DRY obrigatório em todo novo código e em toda refatoração.
2. Nomes de pastas, arquivos, classes, funções e variáveis devem ser claros e autoexplicativos.
3. Cada mudança deve preservar comportamento funcional esperado, exceto quando a mudança for intencional e documentada.
4. Nenhuma fase fecha sem testes mínimos do que foi alterado.
5. Todo erro relevante deve ter log com contexto técnico suficiente para diagnóstico.

## Estrutura-alvo sugerida
```text
cv-generator-automation/
  src/
    cv_generator/
      __init__.py
      cli.py
      application/
        cv_service.py
      domain/
        models.py
        validators.py
        localization.py
      infrastructure/
        config_loader.py
        json_repository.py
        pdf_renderer.py
      shared/
        exceptions.py
        logging_config.py
  tests/
    unit/
    integration/
  scripts/
    start_mac.sh
  config/
    config.json
    styles.json
    translations.json
```

## Fase 1 - Baseline técnico e preparação da refatoração
### Entradas
- Estado atual do repositório.
- Arquivos atuais de configuração e execução.

### Saídas
- Baseline funcional validado.
- Inventário de responsabilidades atuais e mapeamento para módulos alvo.

### Passos ordenados
1. Criar branch de trabalho para a refatoração.
2. Rodar geração PT/EN e registrar comportamento atual (arquivos gerados, tempo, logs).
3. Documentar responsabilidades atuais do `cv_generator.py` por bloco funcional.
4. Definir mapa de migração função por função para a estrutura em `src/`.
5. Definir convenções de naming para arquivos, classes e variáveis.

### Critério de pronto
- Baseline funcional documentado e reproduzível.
- Plano de migração de funções aprovado.
- Convenções de nomenclatura registradas.

### Checklist
- [ ] Branch de refatoração criada.
- [ ] Baseline PT/EN executado e registrado.
- [ ] Mapa de responsabilidades do monólito finalizado.
- [ ] Mapa de migração para módulos finalizado.
- [ ] Convenções de nomes autoexplicativos definidas.
- [ ] Regra DRY registrada como obrigatória no plano de execução.

## Fase 2 - Reorganização de estrutura e separação de responsabilidades
### Entradas
- Mapa de migração validado na Fase 1.

### Saídas
- Estrutura de pastas/módulos criada.
- Código separado por camadas com responsabilidades claras.

### Passos ordenados
1. Criar estrutura `src/cv_generator` e mover entrada de CLI para `cli.py`.
2. Extrair carregamento de configuração para `infrastructure/config_loader.py`.
3. Extrair leitura de JSON para `infrastructure/json_repository.py`.
4. Extrair validação de dados para `domain/validators.py`.
5. Extrair localização/formatação textual para `domain/localization.py`.
6. Extrair geração de PDF para `infrastructure/pdf_renderer.py`.
7. Criar `application/cv_service.py` como orquestrador único.
8. Garantir importações sem ciclos e sem duplicação de lógica.

### Critério de pronto
- Monólito principal desmontado em módulos coesos.
- Cada módulo com responsabilidade única.
- CLI funcionando via camada de aplicação.

### Checklist
- [ ] Estrutura de diretórios nova criada.
- [ ] `cli.py` operacional.
- [ ] `cv_service.py` operacional.
- [ ] `validators.py` operacional.
- [ ] `pdf_renderer.py` operacional.
- [ ] Nenhuma regra de negócio duplicada entre módulos (DRY validado).
- [ ] Nomes de módulos e classes autoexplicativos.

## Fase 3 - Refatoração DRY e padronização de nomes
### Entradas
- Código modular da Fase 2.

### Saídas
- Redução de duplicação.
- Código mais legível e com naming consistente.

### Passos ordenados
1. Consolidar lógica repetida de renderização de seções em um único fluxo configurável.
2. Padronizar assinatura de funções e tipos de retorno.
3. Renomear símbolos ambíguos para nomes descritivos.
4. Centralizar constantes e defaults em módulos próprios.
5. Adicionar tipagem gradual nas funções críticas.
6. Remover código morto, configurações não utilizadas e branches redundantes.

### Critério de pronto
- Não há blocos duplicados relevantes.
- Naming uniforme em todo o projeto.
- Código morto removido sem regressão.

### Checklist
- [ ] Fluxo de seções sem duplicação.
- [ ] Constantes centralizadas.
- [ ] Nomes ambíguos eliminados.
- [ ] Tipagem aplicada nos pontos críticos.
- [ ] Código morto removido.
- [ ] Princípio DRY validado em revisão.

## Fase 4 - Tratamento de erros e robustez operacional
### Entradas
- Módulos refatorados da Fase 3.

### Saídas
- Erros tipados.
- Fluxo de falha previsível e testável.

### Passos ordenados
1. Criar exceções customizadas em `shared/exceptions.py`.
2. Substituir `exit()` dentro de funções internas por exceções específicas.
3. Tratar exceções no ponto de entrada (`cli.py`) com códigos de saída claros.
4. Remover `except Exception` genérico onde houver alternativa específica.
5. Garantir mensagens de erro consistentes para usuário e para log técnico.

### Critério de pronto
- Não existe `exit()` no core da aplicação.
- Exceções são específicas, rastreáveis e testáveis.
- CLI retorna códigos previsíveis em falhas.

### Checklist
- [ ] Exceções customizadas implementadas.
- [ ] `exit()` removido do domínio/aplicação.
- [ ] Tratamento final centralizado na CLI.
- [ ] Capturas genéricas minimizadas.
- [ ] Mensagens de erro padronizadas.

## Fase 5 - Plano de logs com Loguru
### Entradas
- Fluxo de aplicação estabilizado até a Fase 4.

### Saídas
- Logging estruturado centralizado.
- Política de níveis e eventos implementada.

### Passos ordenados
1. Adicionar `loguru` nas dependências.
2. Criar `shared/logging_config.py` com configuração única de logger.
3. Configurar sink de console para desenvolvimento (formato legível).
4. Configurar sink de arquivo rotativo para execução local/CI (`logs/cv_generator.log`).
5. Estruturar contexto mínimo obrigatório por evento: `request_id`, `language`, `input_file`, `output_file`, `step`, `duration_ms`.
6. Instrumentar pontos-chave: carregamento de config, validação, renderização por seção, build do PDF, erros.
7. Padronizar mensagens orientadas a evento (não apenas texto livre).

### Critério de pronto
- Logger inicializa em um único ponto.
- Eventos críticos do fluxo completo estão cobertos.
- Logs permitem diagnosticar falha sem reproduzir manualmente.

### Checklist
- [ ] `loguru` adicionado em dependências.
- [ ] Configuração central de logger criada.
- [ ] Sink de console ativo.
- [ ] Sink de arquivo rotativo ativo.
- [ ] Contexto de execução incluído nos logs.
- [ ] Eventos-chave instrumentados.
- [ ] Logs de erro com stack trace ativo.

## Política de níveis de log (Loguru)
- `DEBUG`: detalhes de desenvolvimento e diagnóstico fino. Usar em parsing, mapeamentos internos e medições de tempo por etapa.
- `INFO`: eventos normais de negócio e progresso da execução. Usar para início/fim de geração, arquivo de saída, seções processadas.
- `WARNING`: anomalias recuperáveis sem interrupção. Usar para seção desconhecida, campo opcional ausente, fallback de idioma.
- `ERROR`: falhas que impedem a conclusão da operação atual. Usar para JSON inválido, arquivo obrigatório ausente, erro de build do PDF.
- `CRITICAL`: falhas sistêmicas que comprometem execução global ou integridade do processo. Usar para erro de inicialização do sistema, configuração inválida sem fallback.

## Eventos mínimos obrigatórios de log
1. `app_start`
2. `config_loaded`
3. `input_validated`
4. `section_render_started`
5. `section_render_finished`
6. `pdf_build_started`
7. `pdf_build_finished`
8. `app_finished`
9. `app_failed`

## Fase 6 - Testes automatizados e cobertura
### Entradas
- Código modular, erros tipados e logging implementados.

### Saídas
- Testes unitários e de integração executando no CI.
- Cobertura mínima definida e monitorada.

### Passos ordenados
1. Criar suíte unitária para validação, localização, sanitização e formatação de período.
2. Criar suíte de integração para geração PT/EN com artefato de PDF.
3. Definir cobertura mínima inicial (exemplo: 70%) com meta de evolução.
4. Configurar execução local via `pytest`.
5. Integrar testes no workflow de CI com falha obrigatória.

### Critério de pronto
- Testes críticos cobrindo fluxo principal.
- CI falha em regressão funcional.
- Cobertura mínima registrada.

### Checklist
- [ ] Testes unitários criados.
- [ ] Testes de integração criados.
- [ ] Cobertura mínima definida.
- [ ] Execução local validada.
- [ ] CI bloqueando regressões.

## Fase 7 - CI, qualidade contínua e documentação final
### Entradas
- Projeto estável com testes e logs.

### Saídas
- Pipeline confiável e documentação atualizada.
- Projeto pronto para manutenção contínua.

### Passos ordenados
1. Ajustar workflow de lint para falhar de forma obrigatória.
2. Incluir checagem de segurança de dependências (`pip-audit`).
3. Revisar `README.md` para refletir estrutura e comandos atuais.
4. Documentar convenções de DRY, naming e logging no repositório.
5. Gerar checklist final de aceite técnico.

### Critério de pronto
- CI validando lint, testes e segurança sem bypass.
- Documentação consistente com o código atual.
- Time consegue executar projeto do zero sem bloqueios.

### Checklist
- [ ] Lint com gate obrigatório.
- [ ] Auditoria de dependências no CI.
- [ ] README atualizado.
- [ ] Convenções registradas.
- [ ] Checklist de aceite final concluído.

## Critérios globais de aceite do plano
- Arquitetura modular implementada e funcionando.
- Código sem duplicação relevante (DRY).
- Nomenclatura clara e autoexplicativa em todo o projeto.
- Logging Loguru ativo com níveis e eventos definidos.
- Testes e CI garantindo qualidade contínua.
