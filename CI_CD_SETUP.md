# 🚀 CI/CD Setup - Documentação

## O que foi configurado?

Este projeto agora possui **dois workflows automáticos no GitHub Actions** que validam o código a cada push/pull request.

---

## 📋 Workflows

### 1. **Test CV Generator** (`.github/workflows/test.yml`)

**Quando dispara:** 
- Toda vez que você faz push em `main` ou `develop`
- Toda vez que você abre um Pull Request para `main`

**O que faz:**
```
✅ Testa em múltiplas versões Python (3.9, 3.10, 3.11)
✅ Valida sintaxe Python do arquivo cv_generator.py
✅ Valida todos os arquivos JSON (cv_data, styles, translations, config)
✅ Gera CV em Português
✅ Gera CV em Inglês
✅ Verifica se os PDFs foram criados com sucesso
✅ Valida tamanho dos PDFs (mínimo 1KB)
```

**Duração:** ~60 segundos por versão Python

---

### 2. **Lint & Code Quality** (`.github/workflows/lint.yml`)

**Quando dispara:**
- Toda vez que você faz push em `main` ou `develop`
- Toda vez que você abre um Pull Request para `main`

**O que faz:**
```
✅ Verifica se o módulo Python é importável
✅ Executa flake8 (linter Python)
✅ Valida encoding UTF-8
✅ Verifica todos os arquivos JSON
✅ Detecta problemas comuns (TODO urgente, print sem logger)
```

**Duração:** ~20 segundos

---

## 🔄 Fluxo de desenvolvimento com CI/CD

### Antes (sem CI/CD):
```
1. Você edita código
2. ❓ Commit/push sem saber se funciona
3. ⏰ Espera alguém testar manualmente
4. ❌ Descobrem erro 3 dias depois
```

### Depois (com CI/CD):
```
1. Você edita código
2. 💾 Commit/push
3. ⚡ GitHub Actions roda automaticamente em 60s
4. 📊 Resultado: ✅ PASSED ou ❌ FAILED
5. 💬 Comentário automático com resultado
```

---

## 📊 Badges de Status

Os badges no README mostram o status atual:

```markdown
[![Test Suite](https://github.com/seu-usuario/cv-generator-automation/actions/workflows/test.yml/badge.svg)](https://github.com/seu-usuario/cv-generator-automation/actions/workflows/test.yml)
```

- **Verde ✅** = Todos os testes passaram
- **Vermelho ❌** = Algum teste falhou

---

## 🎯 Como usar

### Fazer um commit normal

```bash
git add .
git commit -m "Fix: improve fallback logic"
git push origin main
```

**O que acontece:**
1. Push vai para GitHub
2. GitHub Actions é acionado automaticamente
3. Testes rodam em paralelo (3 versões Python)
4. ⏱️ Resultado em ~60-90 segundos
5. 📧 Notificação no GitHub/email se falhar

### Abrir um Pull Request

```bash
git checkout -b minha-feature
# ... edita arquivo ...
git push origin minha-feature
# Abre PR no GitHub
```

**O que acontece:**
1. PR é criado
2. GitHub Actions valida automaticamente
3. Badge de status aparece na PR
4. ✅ Se passou: pode fazer merge tranquilo
5. ❌ Se falhou: precisa corrigir antes de merge

---

## 🔍 Verificando resultados

### No GitHub

1. Vá em **Actions** no seu repositório
2. Veja os workflows em execução ou completados
3. Clique em um workflow para ver detalhes

### Localmente (simular teste)

```bash
# Testar sintaxe Python
python -m py_compile cv_generator.py

# Validar JSON
python -m json.tool cv_data.json
python -m json.tool styles.json
python -m json.tool translations.json
python -m json.tool config.json

# Gerar CVs de teste
python cv_generator.py -l pt
python cv_generator.py -l en

# Verificar se PDFs existem
ls -lh output/*.pdf
```

---

## ✅ Benefícios

| Benefício | Antes | Depois |
|-----------|-------|--------|
| **Detectar erros** | Manual | Automático em 60s ✅ |
| **Múltiplas versões Python** | Testa 1 | Testa 3 (3.9, 3.10, 3.11) ✅ |
| **Validação JSON** | Nenhuma | Automática ✅ |
| **Geração de PDF** | Manual | Automática ✅ |
| **Histórico de testes** | Nenhum | Completo no GitHub ✅ |
| **Confiabilidade** | Questionável | Garantida ✅ |

---

## 🚨 Troubleshooting

### CI/CD falhou. O que fazer?

1. **Clique no workflow que falhou** no GitHub Actions
2. **Veja o erro** na seção "Logs"
3. **Corrija localmente**:
   ```bash
   python -m py_compile cv_generator.py
   python -m json.tool cv_data.json
   ```
4. **Commit e push novamente**

### Erros comuns

**❌ JSON inválido**
```
Error: Expecting value: line 1 column 1
```
→ Verifique vírgulas e aspas em cv_data.json

**❌ PDF não gerado**
```
FileNotFoundError: No such file or directory: 'output/...'
```
→ Verifique se reportlab está instalado

**❌ Python syntax error**
```
SyntaxError: unexpected EOF while parsing
```
→ Verifique se não falta dois-pontos ou aspas

---

## 📝 Próximas melhorias (opcional)

Possíveis adições no futuro:

- ✨ Deploy automático para GitHub Pages
- ✨ Gerar relatório de cobertura de testes
- ✨ Notificações no Slack/Discord
- ✨ Validação de performance
- ✨ Backup automático de PDFs

---

## 📞 Suporte

Se tiver dúvidas sobre CI/CD:

1. Consulte [documentação oficial do GitHub Actions](https://docs.github.com/pt/actions)
2. Veja os logs no GitHub Actions
3. Teste localmente antes de fazer push

---

**Última atualização:** Janeiro 2026  
**Status:** ✅ Ativo e funcional
