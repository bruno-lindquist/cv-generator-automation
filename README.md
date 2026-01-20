# 📄 CV Generator - PDF Resume Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![ReportLab 4.0.9](https://img.shields.io/badge/ReportLab-4.0.9-green.svg)](https://www.reportlab.com/)
[![Test Suite](https://github.com/seu-usuario/cv-generator-automation/actions/workflows/test.yml/badge.svg)](https://github.com/seu-usuario/cv-generator-automation/actions/workflows/test.yml)
[![Code Quality](https://github.com/seu-usuario/cv-generator-automation/actions/workflows/lint.yml/badge.svg)](https://github.com/seu-usuario/cv-generator-automation/actions/workflows/lint.yml)

Professional-grade tool for generating PDF resumes with **complete multilingual support** (Portuguese 🇧🇷 and English 🇬🇧) from structured JSON data. Maintains complete separation between data, styles, and generation logic, allowing full customization without touching code. **Entire codebase now in English** - variable names, functions, and comments fully internationalized.

## ✨ Features

- 🌍 **Automatic Multilingual Support**: Portuguese and English with intelligent fallback (empty EN fields use PT)
- 📊 **Clean Architecture**: Data in `cv_data.json`, styles in `styles.json`, translations in `translations.json`
- 🎨 **100% Customizable**: Colors, fonts, margins, spacing via JSON (zero code needed)
- 💻 **English Codebase**: All variable names, functions, and comments in English for international collaboration
- 📝 **Structured Logging**: Complete error and operation tracking
- ⚡ **Efficient**: Optimized code, no repetition, reusable methods
- 📅 **Smart Dates**: Automatic month formatting (Jan, Feb, Mar... based on language)
- 🚀 **Dual Interface**: Interactive menu (shell/batch) or Python command line
- 🔧 **CI/CD Ready**: Supports CLI arguments for automation

## 📁 Project Structure

```
cv-generator/
├── 📄 config.json              # Central configuration (paths, default language)
├── 📄 cv_data.json             # Your CV data (PT + EN)
├── 📄 styles.json              # Styles and formatting (colors, fonts, spacing)
├── 📄 translations.json        # Multilingual texts (section titles)
├── 🐍 cv_generator.py          # Main generation script
├── 🔧 start_mac.sh             # Interactive menu (macOS/Linux)
├── 🔧 start_windows.bat        # Interactive menu (Windows)
├── 📖 README.md                # This documentation
├── 📋 LICENSE                  # MIT License
├── 📋 requirements.txt         # Python dependencies
├── 🚫 .gitignore               # Files ignored in git
└── 📁 output/                  # Generated PDFs here
```

## 🚀 Quick Start

### 1️⃣ Clonar Repositório
```bash
git clone https://github.com/seu-usuario/cv-generator-automation-.git
cd cv-generator
```

### 2️⃣ Instalar Dependências

**macOS/Linux com script automático:**
```bash
chmod +x start_linux.sh
./start_linux.sh
```

**Windows com script automático:**
```cmd
start_windows.bat
```

**Manual (qualquer SO):**
```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate.bat   # Windows
pip install -r requirements.txt
```

### 3️⃣ Editar Seus Dados
Abra `cv_data.json` e preencha com suas informações pessoais, experiências, educação, etc.

### 4️⃣ Gerar CV

**Menu interativo:**
```bash
./start_linux.sh        # macOS/Linux
# ou
start_windows.bat       # Windows
```

**Por linha de comando:**
```bash
python cv_generator.py              # CV em português
python cv_generator.py -l en        # CV em inglês
python cv_generator.py -l en -o curriculum.pdf  # Output customizado
```

## 📝 Estrutura de Dados (`cv_data.json`)

O arquivo `cv_data.json` contém todas as informações do seu CV. Suporta **seções opcionais** - apenas inclua as que você precisa:

### Informações Pessoais

```json
{
  "personal_info": {
    "name": "Bruno",
    "email": "seu@email.com",
    "phone": "(11) 97894-0000",
    "location": "Sao Paulo, SP",
    "social": [
      { "label": "LinkedIn", "url": "https://linkedin.com/in/seu-perfil" },
      { "label": "GitHub", "url": "https://github.com/seu-usuario" },
      { "label": "Behance", "url": "https://behance.net/seu-portfolio" }
    ]
  }
}
```

### Cargo Desejado

```json
{
  "desired_role": {
    "desired_role_pt": "Python Developer",
    "desired_role_en": "Python Developer"
  }
}
```

### Resumo Profissional

```json
{
  "summary": {
    "description_pt": "Texto em português sobre sua experiência...",
    "description_en": "Text in English about your experience..."
  }
}
```

### Experiência Profissional

```json
{
  "experience": [
    {
      "company_pt": "Empresa XYZ",
      "company_en": "XYZ Company",
      "position_pt": "Desenvolvedor Python Sênior",
      "position_en": "Senior Python Developer",
      "start_month": "1",
      "start_year": "2020",
      "end_month": "12",
      "end_year": "2023",
      "description_pt": [
        "Desenvolveu sistema X com Python",
        "Liderou equipe de 5 desenvolvedores",
        "Implementou pipeline de CI/CD"
      ],
      "description_en": [
        "Developed X system with Python",
        "Led team of 5 developers",
        "Implemented CI/CD pipeline"
      ]
    }
  ]
}
```

### Educação

```json
{
  "education": [
    {
      "institution_pt": "Universidade XYZ",
      "institution_en": "XYZ University",
      "course_pt": "Bacharelado em Ciência da Computação",
      "course_en": "Bachelor's in Computer Science",
      "start_month": "2",
      "start_year": "2016",
      "end_month": "12",
      "end_year": "2020"
    }
  ]
}
```

### Competências

```json
{
  "core_skills": [
    "Python", "Web Scraping", "API REST", "SQL", "Git", "CI/CD"
  ],
  
  "skills": [
    {
      "category_pt": "Backend",
      "category_en": "Backend",
      "items": ["Python", "Django", "FastAPI", "PostgreSQL"]
    },
    {
      "category_pt": "Frontend",
      "category_en": "Frontend",
      "items": ["React", "TypeScript", "CSS3", "HTML5"]
    }
  ]
}
```

### Idiomas

```json
{
  "languages": [
    {
      "language": "Português",
      "level_pt": "Nativo",
      "level_en": "Native"
    },
    {
      "language": "Inglês",
      "level_pt": "Fluente",
      "level_en": "Fluent"
    }
  ]
}
```

### Prêmios e Certificações

```json
{
  "awards": [
    {
      "title_pt": "Melhor Projeto",
      "title_en": "Best Project",
      "issuer_pt": "Hackathon XYZ",
      "issuer_en": "XYZ Hackathon",
      "year": "2021"
    }
  ],
  
  "certifications": [
    {
      "title_pt": "AWS Certified Developer",
      "title_en": "AWS Certified Developer",
      "issuer": "Amazon",
      "year": "2023"
    }
  ]
}
```


Os scripts realizam automaticamente:
1. ✅ Criação de ambiente virtual (se não existir)
2. ✅ Instalação de dependências
3. ✅ Geração do(s) CV(s) no idioma escolhido


## � CI/CD - Automação com GitHub Actions

Este projeto utiliza **GitHub Actions** para validação automática. A cada commit/push:

### ✅ Testes Automáticos (`.github/workflows/test.yml`)

- ✓ Valida sintaxe Python em múltiplas versões (3.9, 3.10, 3.11)
- ✓ Valida JSON de todos os arquivos de configuração
- ✓ Gera CV em Português
- ✓ Gera CV em Inglês
- ✓ Verifica se PDFs foram criados com sucesso
- ✓ Valida tamanho dos PDFs gerados

### 📊 Validação de Código (`.github/workflows/lint.yml`)

- ✓ Verifica imports Python
- ✓ Linting com flake8
- ✓ Validação de encoding UTF-8
- ✓ Detecção de problemas comuns

**Status atual:** 
- [![Test Suite](https://github.com/seu-usuario/cv-generator-automation/actions/workflows/test.yml/badge.svg)](https://github.com/seu-usuario/cv-generator-automation/actions/workflows/test.yml)
- [![Code Quality](https://github.com/seu-usuario/cv-generator-automation/actions/workflows/lint.yml/badge.svg)](https://github.com/seu-usuario/cv-generator-automation/actions/workflows/lint.yml)


## �📦 Dependências

- **Python**: 3.7 ou superior
- **reportlab**: 4.0.9 (para geração de PDF)

```bash
pip install -r requirements.txt
```

## 🤝 Contribuindo

Contribuições são bem-vindas!

## 👨‍💻 Autor

**Bruno Lindquist**
- [LinkedIn](https://www.linkedin.com/in/bruno-lindquist/)
- [GitHub](https://github.com/bruno-lindquist)

## ⭐ Curte o Projeto?

Deixe uma estrela ⭐ no GitHub!

---

**Status:** ✅ Ativo | **Última atualização:** Janeiro 2026

