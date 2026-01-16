# 🤝 Guia de Contribuição

Obrigado por considerar contribuir para o CV Generator! Este documento fornece diretrizes e instruções para contribuir ao projeto.

## Código de Conduta

Esperamos que todos os participantes façam com que este projeto seja um ambiente acolhedor e inclusivo para todos. Por favor, revise nosso [Código de Conduta](CODE_OF_CONDUCT.md).

## Como Começar

### Reportar Bugs

Bugs são rastreados como [GitHub Issues](https://github.com/bruno-lindquist/cv-generator/issues). Ao reportar um bug, por favor:

1. **Use um título descritivo** para o issue
2. **Descreva os passos exatos** para reproduzir o problema
3. **Forneça exemplos específicos** para demonstrar os passos
4. **Descreva o comportamento observado** e o que você esperava ver
5. **Inclua screenshots ou GIFs** se possível
6. **Especifique sua versão** do Python e do sistema operacional

### Sugerir Enhancements

Enhancement suggestions são também rastreadas como [GitHub Issues](https://github.com/bruno-lindquist/cv-generator/issues). Ao sugerir um enhancement:

1. **Use um título descritivo** para a sugestão
2. **Forneça uma descrição detalhada** da feature sugerida
3. **Liste exemplos de uso** para melhor clareza
4. **Explique por que essa feature seria útil**

## Pull Requests

### Processo de Pull Request

1. **Fork o repositório** e crie sua branch do `main`
   ```bash
   git checkout -b feature/sua-feature
   ```

2. **Commit suas mudanças** com mensagens claras
   ```bash
   git commit -m "Adiciona feature X: descrição clara"
   ```

3. **Push para sua fork**
   ```bash
   git push origin feature/sua-feature
   ```

4. **Abra um Pull Request** com uma descrição detalhada

### Diretrizes para Pull Requests

- ✅ **Mantenha o escopo pequeno** - um PR = uma feature ou bug fix
- ✅ **Teste sua mudança** antes de submeter
- ✅ **Siga o estilo de código** do projeto
- ✅ **Inclua mensagens de commit descritivas**
- ✅ **Referencie issues relevantes** usando `#numero`
- ✅ **Atualize documentação** conforme necessário

### Template de PR

```markdown
## Descrição
Breve descrição do que este PR faz.

## Tipo de Mudança
- [ ] Bug fix (non-breaking change que corrige um issue)
- [ ] Nova feature (non-breaking change que adiciona funcionalidade)
- [ ] Breaking change (mudança que interrompe funcionalidade existente)
- [ ] Documentação

## Como Foi Testado
Descreva os testes que você executou.

## Checklist
- [ ] Meu código segue o estilo de código do projeto
- [ ] Atualizei a documentação conforme necessário
- [ ] Testei em Python 3.7+
- [ ] Não criei novos warnings
```

## Estilo de Código

### Python

- Use **PEP 8** como guia
- Nomear variáveis com **snake_case**: `cv_data`, `file_path`
- Nomear classes com **PascalCase**: `CVGenerator`
- Nomear constantes com **UPPER_SNAKE_CASE**: `MONTHS_PT`
- Máximo de **88 caracteres por linha**
- Use **docstrings** em funções públicas

Exemplo:
```python
def _format_month(month_number: int, language: str = "pt") -> str:
    """
    Formata número do mês em abreviação.
    
    Args:
        month_number: Número do mês (1-12)
        language: Idioma ('pt' ou 'en')
    
    Returns:
        Abreviação do mês com 3 letras
    """
    months = MONTHS_PT if language == "pt" else MONTHS_EN
    return months.get(month_number, "")
```

### JSON

- Use **2 espaços** para indentação
- Use **chaves duplas** para strings
- Mantenha estrutura **consistente**

## Desenvolvimento Local

### Setup do Ambiente

```bash
# Clone seu fork
git clone https://github.com/seu-usuario/cv-generator.git
cd cv-generator

# Crie virtualenv
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou source venv/Scripts/activate # Windows

# Instale dependências
pip install -r requirements.txt

# Instale dev dependencies (opcional)
pip install pylint black pytest
```

### Testando Localmente

```bash
# Teste em português
python cv_generator.py

# Teste em inglês
python cv_generator.py -l en

# Valide seu código
python -m pylint cv_generator.py
```

## Commit Messages

Use mensagens de commit claras e descritivas:

```
Adiciona: descrição clara (para novas features)
Corrige: descrição clara (para bug fixes)
Documenta: descrição clara (para atualizações de docs)
Refatoração: descrição clara (para refactorings)
Testa: descrição clara (para novos testes)
```

Exemplos:

```
✅ Adiciona suporte a múltiplos templates
✅ Corrige fallback de idioma em campos vazios
✅ Documenta uso de espaçamentos em mm
❌ atualiza
❌ fix bug
```

## Adicionando Novas Features

Se você quer adicionar uma feature:

1. **Abra um issue primeiro** para discussão
2. **Espere feedback** antes de começar
3. **Implemente a feature** em uma branch
4. **Inclua testes** se aplicável
5. **Atualize documentação**
6. **Envie um PR** com referência ao issue

## Reportando Vulnerabilidades de Segurança

**NÃO** abra um GitHub Issue para vulnerabilidades de segurança. Em vez disso, envie um email para bruno@seu-email.com.

## Licença

Ao contribuir para este projeto, você concorda que suas contribuições serão licenciadas sob a mesma [Licença MIT](../LICENSE).

## Perguntas?

Sinta-se livre para entrar em contato:
- 📧 Email: bruno@seu-email.com
- 💬 Abra uma [Discussion](https://github.com/bruno-lindquist/cv-generator/discussions)
- 🐛 [Issues](https://github.com/bruno-lindquist/cv-generator/issues)

---

**Obrigado por contribuir!** 🎉
