# 📄 CV Generator - Gerador de Currículo em PDF

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Ferramenta elegante para gerar currículos profissionais em PDF com suporte multilíngue (Português 🇧🇷 e Inglês 🇬🇧) usando dados estruturados em JSON. Separação completa entre dados, estilos e lógica.

## ✨ Características

- 🌍 **Multilíngue**: Suporte total para português e inglês com fallback automático
- 📊 **Separação de responsabilidades**: Dados, estilos e configurações em arquivos JSON separados
- 🎨 **Totalmente customizável**: Cores, fontes, margens, espaçamentos 100% configuráveis via JSON
- 📝 **Logging integrado**: Rastreamento completo de erros e informações de geração
- ⚡ **Otimizado**: Código limpo, sem repetições, métodos genéricos
- 🔄 **Fallback automático**: Campo em inglês vazio? Usa português automaticamente
- 📅 **Formatação inteligente**: Meses automaticamente abreviados conforme idioma (Jan, Fev, etc)
- 🚀 **Fácil de usar**: Menu interativo ou linha de comando

## 📁 Estrutura do Projeto

```
cv-generator/
├── 📄 config.json              # Configuração central (caminhos, idioma padrão)
├── 📄 cv_data.json             # Seus dados do CV (PT + EN)
├── 📄 styles.json              # Estilos e formatação (cores, fonts, spacing)
├── 📄 translations.json        # Textos multilíngues (títulos de seções)
├── 🐍 cv_generator.py          # Script principal de geração
├── 🔧 cv.sh                    # Menu interativo (macOS/Linux)
├── 🔧 cv.bat                   # Menu interativo (Windows)
├── 📖 README.md                # Esta documentação
├── 📋 LICENSE                  # MIT License
├── 📋 requirements.txt         # Dependências Python
├── 🚫 .gitignore               # Arquivos ignorados no git
└── 📁 output/                  # PDFs gerados aqui
```

## 🚀 Quick Start

### 1️⃣ Clonar Repositório
```bash
git clone https://github.com/seu-usuario/cv-generator.git
cd cv-generator
```

### 2️⃣ Instalar Dependências
```bash
# Com script automático (macOS/Linux)
chmod +x cv.sh
./cv.sh

# Ou manualmente
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# source venv/Scripts/activate # Windows
pip install -r requirements.txt
```

### 3️⃣ Editar Dados
Abra `cv_data.json` e preencha com suas informações

### 4️⃣ Gerar CV
```bash
# Menu interativo
./cv.sh

# Ou por linha de comando
python cv_generator.py           # Gera em português
python cv_generator.py -l en     # Gera em inglês
```

## 📋 Configuração

### `config.json` - Centro de Controle
```json
{
  "files": {
    "data": "cv_data.json",
    "styles": "styles.json",
    "translations": "translations.json",
    "output_dir": "output"
  },
  "defaults": {
    "language": "pt",
    "encoding": "utf-8"
  },
  "logging": {
    "enabled": true,
    "level": "info"
  }
}
```

### `styles.json` - Customização Visual
Todas as medidas em **milímetros (mm)**:

```json
{
  "margins": { "top": 19, "bottom": 19, "left": 19, "right": 19 },
  "spacing": {
    "header_bottom": 5,
    "section_bottom": 4,
    "item_bottom": 3,
    "small_bottom": 2,
    "minimal_bottom": 1
  },
  "colors": {
    "name": "#1a1a1a",
    "section_title": "#2c3e50",
    "text": "#404040"
  },
  "fonts": {
    "name_size": 24,
    "title_size": 12,
    "section_size": 13,
    "subheading_size": 11,
    "body_size": 10
  }
}
```

### `translations.json` - Textos Multilíngues
```json
{
  "pt": {
    "sections": {
      "summary": "RESUMO",
      "experience": "EXPERIÊNCIA PROFISSIONAL",
      "education": "FORMAÇÃO ACADÊMICA",
      "core_skills": "CONHECIMENTOS",
      "skills": "HABILIDADES",
      "languages": "IDIOMAS",
      "awards": "PRÊMIOS E RECONHECIMENTOS",
      "certifications": "CERTIFICAÇÕES"
    },
    "labels": {
      "current": "(até o momento)"
    }
  },
  "en": {
    "sections": {
      "summary": "SUMMARY",
      "experience": "PROFESSIONAL EXPERIENCE",
      "education": "EDUCATION",
      "core_skills": "CORE SKILLS",
      "skills": "SKILLS",
      "languages": "LANGUAGES",
      "awards": "AWARDS",
      "certifications": "CERTIFICATIONS"
    },
    "labels": {
      "current": "(present)"
    }
  }
}
```

### `cv_data.json` - Seus Dados
Exemplo de estrutura completa:

```json
{
  "personal_info": {
    "name": "Seu Nome",
    "email": "seu@email.com",
    "phone": "+55 (11) 9999-9999",
    "location": "Cidade, Estado",
    "social": [
      { "label": "LinkedIn", "url": "https://linkedin.com/in/seu-perfil" },
      { "label": "GitHub", "url": "https://github.com/seu-usuario" }
    ]
  },
  "desired_role_pt": "Desenvolvedor Python",
  "desired_role_en": "Python Developer",
  "summary_pt": "Profissional com experiência em...",
  "summary_en": "Professional with experience in...",
  "experience": [
    {
      "company_pt": "Empresa XYZ",
      "company_en": "XYZ Company",
      "position_pt": "Desenvolvedor Python",
      "position_en": "Python Developer",
      "start_month": "1",
      "start_year": "2020",
      "end_month": "12",
      "end_year": "2023",
      "description_pt": ["Desenvolveu sistema X", "Liderou equipe Y"],
      "description_en": ["Developed system X", "Led team Y"]
    }
  ]
}
```

## 💻 Uso Avançado

### Linha de Comando
```bash
# Gerar CV em português
python cv_generator.py

# Gerar CV em inglês
python cv_generator.py -l en

# Especificar arquivo de saída
python cv_generator.py -o meu_cv_2024.pdf

# Usar configuração customizada
python cv_generator.py -c config_alternativo.json

# Combinar opções
python cv_generator.py -l en -o curriculum_en.pdf -c config_custom.json
```

### Scripts Interativos

**macOS/Linux:**
```bash
chmod +x cv.sh
./cv.sh              # Menu interativo
./cv.sh pt           # Apenas português
./cv.sh en           # Apenas inglês
./cv.sh todas        # Ambas versões
```

**Windows:**
```cmd
cv.bat              # Menu interativo
cv.bat pt           # Apenas português
cv.bat en           # Apenas inglês
cv.bat todas        # Ambas versões
```

## 🎨 Personalizando Seu CV

### Mudar Cores
Edite `styles.json`:
```json
"colors": {
  "name": "#000000",           # Seu nome
  "section_title": "#0066cc",  # Títulos de seção
  "text": "#333333"            # Texto do corpo
}
```

### Ajustar Espaçamentos
Todos em milímetros (1 mm ≈ 2.83 pixels):
```json
"spacing": {
  "header_bottom": 5,    # Espaço após cabeçalho
  "section_bottom": 4,   # Espaço após seção
  "item_bottom": 3,      # Espaço entre itens
  "small_bottom": 2,
  "minimal_bottom": 1
}
```

### Customizar Fontes
Tamanhos em pontos:
```json
"fonts": {
  "name_size": 24,
  "title_size": 12,
  "section_size": 13,
  "subheading_size": 11,
  "body_size": 10
}
```

## 🌍 Suporte Multilíngue

O sistema usa fallback automático para campos em inglês vazios:

```json
{
  "position_pt": "Desenvolvedor Python",
  "position_en": ""  // Automaticamente usa position_pt
}
```

**Formatação de datas:** As datas são formatadas em 3 letras conforme idioma (Jan, Fev...) ou (Jan, Feb...)

## 📦 Dependências

- Python 3.7+
- reportlab 4.0.9

```bash
pip install -r requirements.txt
```

## 🐛 Troubleshooting

### JSON inválido
```bash
python3 -m json.tool cv_data.json
```

### Arquivo não encontrado
```bash
ls -la config.json cv_data.json styles.json translations.json
```

### Ver logs detalhados
```bash
python cv_generator.py 2>&1 | head -20
```

## 🤝 Contribuindo

Contribuições são bem-vindas!

```bash
git checkout -b feature/minha-melhoria
git commit -am 'Descreve sua mudança'
git push origin feature/minha-melhoria
```

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Bruno Lindquist**
- [LinkedIn](https://www.linkedin.com/in/bruno-lindquist/)
- [GitHub](https://github.com/bruno-lindquist)

## ⭐ Curte o Projeto?

Deixe uma estrela ⭐ no GitHub!

---

**Status:** ✅ Ativo | **Última atualização:** Janeiro 2026

