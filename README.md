# CV Generator - Automated PDF Resume Creation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![ReportLab 4.0.9](https://img.shields.io/badge/ReportLab-4.0.9-green.svg)](https://www.reportlab.com/)

Generate professional PDF resumes from structured JSON data with complete bilingual support (Portuguese & English). No code modifications needed—customize everything through JSON configuration files.

## Features

- **Bilingual Support**: Automatically generate PDFs in Portuguese or English from the same data
- **Separation of Concerns**: Data, styles, and translations in separate JSON files
- **JSON-Only Customization**: Colors, fonts, spacing—all configurable without touching code
- **Interactive & CLI Modes**: Choose between guided menu or command-line interface
- **Structured Data Format**: Validated JSON schema for reliable CV generation
- **Smart Formatting**: Automatic date formatting and multilingual month names
- **Cross-Platform**: Works on macOS, Linux, and Windows

## Project Structure

```
cv-generator-automation/
├── config.json                 # Central configuration (paths, language defaults)
├── cv_data.json                # Your CV data (Portuguese + English)
├── styles.json                 # Visual styling (colors, fonts, spacing)
├── translations.json           # Multilingual text labels
├── cv_generator.py             # Main generation script
├── start_mac.sh                # Quick start for macOS/Linux
├── start_windows.bat           # Quick start for Windows
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation
├── LICENSE                     # MIT License
└── output/                     # Generated PDFs
```

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/bruno-lindquist/cv-generator-automation.git
cd cv-generator-automation
```

### 2. Install Dependencies

**macOS/Linux:**
```bash
chmod +x start_mac.sh
./start_mac.sh
```

**Windows:**
```cmd
start_windows.bat
```

**Manual Installation (any OS):**
```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate.bat   # Windows
pip install -r requirements.txt
```

### 3. Configure Your CV

Edit `cv_data.json` with your personal information, experience, education, and skills.

### 4. Generate PDF

**Interactive Menu:**
```bash
./start_mac.sh          # macOS/Linux
# or
start_windows.bat       # Windows
```

**Command Line:**
```bash
python cv_generator.py              # Portuguese
python cv_generator.py -l en        # English
python cv_generator.py -l en -o resume.pdf  # Custom output
```

## Configuration Guide

### cv_data.json

The main data file contains all your CV information. Include only the sections you need.

**Personal Information:**
```json
{
  "personal_info": {
    "name": "Bruno",
    "email": "your@email.com",
    "phone": "+55 11 97894-0000",
    "location": "São Paulo, SP",
    "social": [
      { "label": "LinkedIn", "url": "https://linkedin.com/in/your-profile" },
      { "label": "GitHub", "url": "https://github.com/your-username" }
    ]
  }
}
```

**Professional Summary:**
```json
{
  "summary": {
    "description_pt": "Experiência em Python e desenvolvimento web...",
    "description_en": "Experience in Python and web development..."
  }
}
```

**Work Experience:**
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
        "Liderou equipe de 5 desenvolvedores"
      ],
      "description_en": [
        "Developed X system with Python",
        "Led team of 5 developers"
      ]
    }
  ]
}
```

**Education:**
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

**Skills:**
```json
{
  "skills": [
    {
      "category_pt": "Backend",
      "category_en": "Backend",
      "items": ["Python", "Django", "FastAPI", "PostgreSQL"]
    },
    {
      "category_pt": "Frontend",
      "category_en": "Frontend",
      "items": ["React", "TypeScript", "CSS3"]
    }
  ]
}
```

**Languages:**
```json
{
  "languages": [
    {
      "language": "Português",
      "level_pt": "Nativo",
      "level_en": "Native"
    },
    {
      "language": "English",
      "level_pt": "Fluente",
      "level_en": "Fluent"
    }
  ]
}
```

### styles.json

Customize visual appearance:
- Colors and fonts
- Margins and spacing
- Text sizes and weights

### translations.json

Multilingual section titles and labels automatically applied based on selected language.

## Requirements

- **Python**: 3.7+
- **reportlab**: 4.0.9 (PDF generation)
- **python-dateutil**: 2.8.0+ (date handling)

All dependencies are listed in `requirements.txt` and installed automatically.

## Usage Examples

**Generate Portuguese CV:**
```bash
python cv_generator.py
```

**Generate English CV:**
```bash
python cv_generator.py -l en
```

**Custom Output File:**
```bash
python cv_generator.py -l en -o my_resume.pdf
```

## Development

### Project Structure

The codebase follows clean architecture principles:
- Data layer: JSON configuration files
- Logic layer: `cv_generator.py` with modular functions
- Presentation layer: ReportLab PDF generation

### Extending the Project

To add new sections or customize styling:

1. **Add data** to `cv_data.json`
2. **Update styles** in `styles.json`
3. **Add translations** to `translations.json`
4. Regenerate PDF

No Python code changes needed.

## Troubleshooting

**"Module not found" error:**
Ensure you've activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**PDF generation fails:**
Check that `cv_data.json` is valid JSON and all required fields are present.

**Wrong language output:**
Verify the language code in your command (`-l pt` or `-l en`).

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details

## Author

**Bruno Lindquist**
- [LinkedIn](https://www.linkedin.com/in/bruno-lindquist/)
- [GitHub](https://github.com/bruno-lindquist)

---

**Status:** Active | **Last Updated:** January 2026
