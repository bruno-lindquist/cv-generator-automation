# CV Generator - Gerador Automático de Currículos em PDF

Gere **currículos profissionais em PDF** de forma rápida e fácil usando **apenas dados em JSON**. Suporte completo para **português e inglês** — sem necessidade de modificar código!

---

## 📋 O Que É?

Um gerador automático de currículos que transforma seus dados estruturados em um PDF bem formatado. Você só precisa editar um arquivo JSON com suas informações profissionais. Pronto! O sistema cuida do resto — layout, formatação, bilíngue, tudo automático.

**Nenhuma codificação necessária.** Tudo é configurado via JSON.

---

## ✨ Por Que Usar?

| Benefício | Descrição |
|-----------|-----------|
| **Sem Código** | Edite apenas JSON, sem tocar em Python |
| **Bilíngue** | Gere PT e EN do mesmo arquivo, automaticamente |
| **Rápido** | Configure em 5 minutos, gere em 2 segundos |
| **Profissional** | Layout limpo e otimizado para ATS |
| **Flexível** | Customize cores, espaçamento, fontes |
| **Reutilizável** | Atualize dados, regenere PDFs ilimitadamente |

---

## 🎯 Vantagens

✅ **Sem Duplicação** - Um único arquivo JSON para português e inglês  
✅ **Separação Clara** - Dados, estilos e traduções em arquivos diferentes  
✅ **Fácil de Manter** - Adicione/remova seções sem mexer no código  
✅ **Compatível** - macOS, Linux, Windows  
✅ **Formatação Rica** - Suporte para **negrito**, *itálico* e <u>sublinhado</u>  
✅ **Datas Inteligentes** - Conversão automática de números em meses (1→Jan, 2→Fev, etc)

---

## 📦 Tecnologias

| Tecnologia | Versão | Propósito |
|------------|--------|----------|
| Python | 3.7+ | Linguagem principal |
| ReportLab | 4.0.9 | Geração de PDFs |
| python-dateutil | 2.8.0+ | Manipulação de datas |
| JSON | — | Armazenamento de dados |

---

## 🏗️ Estrutura do Projeto

```
cv-generator-automation/
├── cv_generator.py          # Motor principal (870+ linhas, bem estruturado)
├── cv_data.json             # Seus dados de CV (PT + EN)
├── styles.json              # Configuração visual (margens, espaçamento)
├── translations.json        # Rótulos multilingues
├── config.json              # Configuração central (caminhos, idioma padrão)
├── requirements.txt         # Dependências Python
├── setup.sh                 # Script de instalação (macOS/Linux)
├── start_mac.sh             # Atalho para gerar ambas as versões
├── start_windows.bat        # Equivalente para Windows
├── README.md                # Este arquivo
└── output/                  # Pasta onde os PDFs são salvos
```

---

## 📚 Módulos Principais

### 1. **CVGenerator** (cv_generator.py)
Classe principal que orquestra todo o processo:
- Carregamento de arquivos JSON
- Validação de dados
- Criação de estilos PDF
- Montagem de seções
- Geração do PDF final

### 2. **Localizador de Dados** (_get_localized_field)
Busca automaticamente valores em português ou inglês:
```
Se procura "position_en" → tenta "position_en" → depois "position_pt" → finalmente "position"
```

### 3. **Formatadores de Seções**
Cada tipo de seção tem seu formatador:
- `_format_experience_item` - Experiência profissional
- `_format_education_item` - Educação
- `_format_skills_item` - Habilidades técnicas
- `_format_language_item` - Idiomas
- `_format_certification_item` - Certificações
- `_format_award_item` - Prêmios

### 4. **Sistema de Tags**
Suporta formatação de texto:
- `<b>Negrito</b>`
- `<i>Itálico</i>`
- `<u>Sublinhado</u>`

---

## 🚀 Como Instalar

### 1️⃣ Clone ou Baixe o Projeto
```bash
git clone https://github.com/bruno-lindquist/cv-generator-automation.git
cd cv-generator-automation
```

### 2️⃣ Instale as Dependências

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows (PowerShell):**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Manual (qualquer OS):**
```bash
python3 -m venv venv           # Criar ambiente virtual
source venv/bin/activate        # Ativar (macOS/Linux)
# venv\Scripts\activate.bat    # Ativar (Windows)
pip install -r requirements.txt # Instalar dependências
```

---

## 💻 Como Usar

### Opção 1: Automático (Gera PT + EN)
```bash
./start_mac.sh          # macOS/Linux
# ou
start_windows.bat       # Windows
```
Gera ambas as versões automaticamente: `Nome_Cargo.pdf` e `Nome_Cargo_EN.pdf`

### Opção 2: Linha de Comando

**Gerar em Português:**
```bash
python cv_generator.py
```

**Gerar em Inglês:**
```bash
python cv_generator.py -l en
```

**Com Nome Customizado:**
```bash
python cv_generator.py -l en -o meu_curriculo.pdf
```

**Opções Disponíveis:**
```
-l, --language    Idioma: pt (padrão) ou en
-o, --output      Nome do arquivo de saída
-c, --config      Arquivo de configuração (padrão: config.json)
```

---

## 📋 Seções Suportadas

O sistema suporta estas seções (todas opcionais):

| Seção                   | Campo JSON        | Descrição |
|-------                  |-----------        |-----------|
| Resumo                  | `summary`         | Descrição profissional |
| Experiência             | `experience`      | Histórico de trabalho |
| Educação                | `education`       | Formação acadêmica |
| Competências Principais | `core_skills`     | Habilidades principais com descrições |
| Habilidades             | `skills`          | Categorias de skills técnicas |
| Idiomas                 | `languages`       | Proficiência em idiomas |
| Prêmios                 | `awards`          | Reconhecimentos e prêmios |
| Certificações           | `certifications`  | Certificados profissionais |

---

## ⚙️ Configuração Avançada

### Ativar/Desativar Seções

No `cv_data.json`, use o array `sections`:

```json
{
  "sections": [
    {"type": "experience", "enabled": true, "order": 1},
    {"type": "education", "enabled": true, "order": 2},
    {"type": "skills", "enabled": true, "order": 3},
    {"type": "languages", "enabled": false, "order": 4},
    {"type": "awards", "enabled": false, "order": 5}
  ]
}
```
