#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Script para gerar CV em PDF a partir de dados em JSON
# Suporta múltiplos idiomas (PT, EN) em um único arquivo de dados

import json
import os
import logging
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


class CVGenerator:
    """Gerador de CV em PDF com suporte multilíngue"""
    
    # Meses abreviados em PT e EN
    MONTHS_PT = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    def __init__(self, json_file=None, language='pt', output_file=None, config_file='config.json'):
        """Inicializa o gerador de CV"""
        self.config = self._load_config(config_file)
        self._setup_logging()
        
        # Usa valores padrão do config se não informados
        self.json_file = json_file or self.config['files']['data']
        self.language = language.lower()
        self.config_file = config_file
        
        self.data = self._load_json(self.json_file)
        self.settings = self._load_json(self.config['files']['styles'])
        self.translations = self._load_json(self.config['files']['translations'])
        
        self._validate_data()
        self.output_file = output_file or self._generate_output_filename()
        
        self.logger.info(f"CVGenerator inicializado: idioma={language}, arquivo={self.json_file}")
    
    def _setup_logging(self):
        """Configura logging"""
        log_config = self.config.get('logging', {})
        level = logging.INFO if log_config.get('enabled', True) else logging.WARNING
        
        logging.basicConfig(
            level=level,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_file):
        """Carrega arquivo de configuração"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: Arquivo de configuração '{config_file}' não encontrado")
            exit(1)
        except json.JSONDecodeError:
            print(f"Erro: Arquivo de configuração JSON inválido")
            exit(1)
    
    def _load_json(self, filepath):
        """Carrega arquivo JSON genérico"""
        try:
            with open(filepath, 'r', encoding=self.config['defaults']['encoding']) as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Arquivo '{filepath}' não encontrado")
            exit(1)
        except json.JSONDecodeError:
            self.logger.error(f"Arquivo '{filepath}' JSON inválido")
            exit(1)
    
    def _validate_data(self):
        """Valida dados obrigatórios"""
        errors = []
        
        if 'personal_info' not in self.data:
            errors.append("• Falta seção 'personal_info'")
        elif 'name' not in self.data['personal_info'] or 'email' not in self.data['personal_info']:
            errors.append("• Falta 'personal_info.name' ou 'personal_info.email'")
        
        if 'desired_role' not in self.data:
            errors.append("• Falta seção 'desired_role'")
        
        if errors:
            self.logger.error("Arquivo cv_data.json inválido!")
            for error in errors:
                self.logger.error(error)
            exit(1)
        
        self.logger.info("Dados validados com sucesso")
    
    def _generate_output_filename(self):
        """Gera nome do arquivo de saída"""
        output_dir = self.config['files']['output_dir']
        Path(output_dir).mkdir(exist_ok=True)
        
        name = self.data['personal_info']['name'].replace(' ', '_')
        desired_role = self._get_localized_field(self.data['desired_role'], 'desired_role', 'CV')
        desired_role = desired_role.replace(' ', '_')
        
        lang_suffix = f"_{self.language.upper()}" if self.language != 'pt' else ""
        return f"{output_dir}/{name}_{desired_role}{lang_suffix}.pdf"
    
    def _get_text(self, key, section=None):
        """Obtém texto de tradução"""
        if section:
            return self.translations.get(self.language, {}).get(section, {}).get(key, key)
        return key
    
    def _escape_text(self, text):
        """Escapa texto para uso seguro em Paragraph"""
        return escape(str(text), {"'": "&apos;", '"': "&quot;"})
    
    def _format_month(self, month_str):
        """Converte número do mês em abreviação"""
        try:
            month_num = int(month_str)
            if 1 <= month_num <= 12:
                months = self.MONTHS_PT if self.language == 'pt' else self.MONTHS_EN
                return months[month_num - 1]
        except (ValueError, IndexError):
            pass
        return month_str
    
    def _get_localized_field(self, data, field_name, default=''):
        """Obtém campo localizado com fallback para português"""
        if not isinstance(data, dict):
            return default
        
        localized_field = f"{field_name}_{self.language}"
        value = data.get(localized_field, '')
        
        if not value and self.language != 'pt':
            value = data.get(f"{field_name}_pt", '')
        
        return value or default
    
    def _format_period(self, start_month, start_year, end_month, end_year):
        """Formata período com mês e ano"""
        start_month = self._format_month(start_month)
        period = f"{start_month}/{start_year}"
        
        if end_month and end_year:
            end_month = self._format_month(end_month)
            period += f" - {end_month}/{end_year}"
        else:
            current_label = self._get_text('current', 'labels')
            period += f" - {current_label}"
        
        return period
    
    def _create_styles(self):
        """Cria estilos personalizados"""
        styles = getSampleStyleSheet()
        colors_cfg = self.settings.get('colors', {})
        fonts_cfg = self.settings.get('fonts', {})
        
        styles.add(ParagraphStyle(
            name='NameStyle',
            parent=styles['Heading1'],
            fontSize=fonts_cfg.get('name_size', 24),
            textColor=colors.HexColor(colors_cfg.get('name', '#1a1a1a')),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='TitleStyle',
            parent=styles['Normal'],
            fontSize=fonts_cfg.get('title_size', 12),
            textColor=colors.HexColor(colors_cfg.get('section_title', '#2c3e50')),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        styles.add(ParagraphStyle(
            name='SectionStyle',
            parent=styles['Heading2'],
            fontSize=fonts_cfg.get('section_size', 13),
            textColor=colors.HexColor(colors_cfg.get('section_title', '#2c3e50')),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='SubheadingStyle',
            parent=styles['Heading3'],
            fontSize=fonts_cfg.get('subheading_size', 11),
            textColor=colors.HexColor(colors_cfg.get('section_title', '#2c3e50')),
            spaceAfter=4,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='BodyStyle',
            parent=styles['Normal'],
            fontSize=fonts_cfg.get('body_size', 10),
            textColor=colors.HexColor(colors_cfg.get('text', '#404040')),
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        return styles
    
    def _format_contact_info(self):
        """Formata informações de contato"""
        info = self.data['personal_info']
        contact_items = []
        
        if info.get('email'):
            contact_items.append(info['email'])
        if info.get('phone'):
            contact_items.append(info['phone'])
        if info.get('location'):
            contact_items.append(info['location'])
        
        return ' | '.join(contact_items)
    
    def _add_header(self, story, styles):
        """Adiciona cabeçalho"""
        info = self.data['personal_info']
        spacing = self.settings['spacing']
        
        story.append(Paragraph(self._escape_text(info['name']), styles['NameStyle']))
        
        title = self._get_localized_field(self.data['desired_role'], 'desired_role')
        if title:
            story.append(Paragraph(self._escape_text(title), styles['TitleStyle']))
        
        story.append(Paragraph(self._escape_text(self._format_contact_info()), styles['BodyStyle']))
        
        links = []
        social_items = info.get('social') or []
        if social_items:
            for item in social_items:
                label = item.get('label', 'Link')
                url = item.get('url', '')
                if url:
                    links.append(f"{label}: {url}")
        
        if links:
            story.append(Paragraph(self._escape_text(' | '.join(links)), styles['BodyStyle']))
        
        story.append(Spacer(1, spacing['header_bottom'] * mm))
    
    def _add_summary(self, story, styles):
        """Adiciona resumo profissional"""
        summary_data = self.data.get('summary', {})
        summary = self._get_localized_field(summary_data, 'description').strip()
        
        if not summary:
            return
        
        spacing = self.settings['spacing']
        section_title = self._get_text('summary', 'sections')
        
        story.append(Paragraph(section_title, styles['SectionStyle']))
        safe_summary = self._escape_text(summary).replace('\n', '<br/>')
        story.append(Paragraph(safe_summary, styles['BodyStyle']))
        story.append(Spacer(1, spacing['section_bottom'] * mm))
    
    def _add_section_items(self, story, styles, section_key, items, item_formatter):
        """Método genérico para adicionar seções com múltiplos itens"""
        if not items:
            return
        
        spacing = self.settings['spacing']
        section_title = self._get_text(section_key, 'sections')
        
        story.append(Paragraph(section_title, styles['SectionStyle']))
        
        for item in items:
            item_formatter(story, styles, item)
        
        story.append(Spacer(1, spacing['item_bottom'] * mm))
    
    def _format_experience_item(self, story, styles, job):
        """Formata item de experiência"""
        spacing = self.settings['spacing']
        
        position = self._get_localized_field(job, 'position')
        company = self._get_localized_field(job, 'company')
        period = self._format_period(
            job.get('start_month', ''),
            job.get('start_year', ''),
            job.get('end_month', ''),
            job.get('end_year', '')
        )
        
        title_text = f"<b>{self._escape_text(position)}</b> - {self._escape_text(company)}"
        story.append(Paragraph(title_text, styles['SubheadingStyle']))
        story.append(Paragraph(self._escape_text(period), styles['BodyStyle']))
        
        descriptions = job.get(f'description_{self.language}') or job.get('description_pt', [])
        for desc in descriptions:
            story.append(Paragraph(f"• {self._escape_text(desc)}", styles['BodyStyle']))
        
        story.append(Spacer(1, spacing['small_bottom'] * mm))
    
    def _format_education_item(self, story, styles, edu):
        """Formata item de educação"""
        spacing = self.settings['spacing']
        
        degree = self._get_localized_field(edu, 'degree')
        institution = self._get_localized_field(edu, 'institution')
        period = self._format_period(
            edu.get('start_month', ''),
            edu.get('start_year', ''),
            edu.get('end_month', ''),
            edu.get('end_year', '')
        )
        
        title_text = f"<b>{self._escape_text(degree)}</b> - {self._escape_text(institution)}"
        story.append(Paragraph(title_text, styles['SubheadingStyle']))
        
        if period.strip():
            story.append(Paragraph(self._escape_text(period), styles['BodyStyle']))
        
        descriptions = edu.get(f'description_{self.language}') or edu.get('description_pt', [])
        for note in descriptions:
            story.append(Paragraph(f"• {self._escape_text(note)}", styles['BodyStyle']))
        
        story.append(Spacer(1, spacing['small_bottom'] * mm))
    
    def _format_core_skills_item(self, story, styles, skill_group):
        """Formata item de competências principais"""
        category = self._get_localized_field(skill_group, 'category')
        descriptions = skill_group.get(f'description_{self.language}') or skill_group.get('description_pt', [])
        
        if category:
            story.append(Paragraph(self._escape_text(category), styles['SubheadingStyle']))
        
        for item in descriptions:
            story.append(Paragraph(f"• {self._escape_text(item)}", styles['BodyStyle']))
        
        story.append(Spacer(1, self.settings['spacing']['minimal_bottom'] * mm))
    
    def _format_skills_item(self, story, styles, skill_group):
        """Formata item de habilidades técnicas"""
        category = self._get_localized_field(skill_group, 'category')
        items = skill_group.get('item', [])
        
        if category:
            story.append(Paragraph(self._escape_text(category), styles['SubheadingStyle']))
        
        for item in items:
            story.append(Paragraph(f"• {self._escape_text(item)}", styles['BodyStyle']))
        
        story.append(Spacer(1, self.settings['spacing']['item_bottom'] * mm))
    
    def _format_language_item(self, story, styles, lang):
        """Formata item de idioma"""
        language = self._get_localized_field(lang, 'language')
        proficiency = self._get_localized_field(lang, 'proficiency')
        
        lang_text = f"<b>{self._escape_text(language)}</b> - {self._escape_text(proficiency)}"
        story.append(Paragraph(lang_text, styles['BodyStyle']))
    
    def _format_award_item(self, story, styles, award):
        """Formata item de prêmio"""
        award_title = self._get_localized_field(award, 'title')
        description = self._get_localized_field(award, 'description')
        
        if award_title and description:
            award_text = f"<b>{self._escape_text(award_title)}</b> - {self._escape_text(description)}"
        else:
            award_text = self._escape_text(award_title or description)
        
        if award_text:
            story.append(Paragraph(award_text, styles['BodyStyle']))
    
    def _format_certification_item(self, story, styles, cert):
        """Formata item de certificação"""
        name = self._get_localized_field(cert, 'name')
        issuer = self._get_localized_field(cert, 'issuer')
        year = cert.get('year', '')
        
        if name and issuer and year:
            cert_text = f"<b>{self._escape_text(name)}</b> - {self._escape_text(issuer)} ({self._escape_text(year)})"
        elif name and issuer:
            cert_text = f"<b>{self._escape_text(name)}</b> - {self._escape_text(issuer)}"
        else:
            cert_text = self._escape_text(name or issuer)
        
        if cert_text:
            story.append(Paragraph(cert_text, styles['BodyStyle']))
    
    def generate(self):
        """Gera o documento PDF"""
        Path(self.config['files']['output_dir']).mkdir(exist_ok=True)
        margins_cfg = self.settings.get('margins', {})
        
        doc = SimpleDocTemplate(
            self.output_file,
            pagesize=A4,
            rightMargin=margins_cfg.get('right', 19) * mm,
            leftMargin=margins_cfg.get('left', 19) * mm,
            topMargin=margins_cfg.get('top', 19) * mm,
            bottomMargin=margins_cfg.get('bottom', 19) * mm
        )
        
        story = []
        styles = self._create_styles()
        
        self._add_header(story, styles)
        self._add_summary(story, styles)
        
        # Adiciona seções usando método genérico
        self._add_section_items(
            story, styles, 'experience',
            self.data.get('experience', []),
            self._format_experience_item
        )
        
        self._add_section_items(
            story, styles, 'education',
            self.data.get('education', []),
            self._format_education_item
        )
        
        self._add_section_items(
            story, styles, 'core_skills',
            self.data.get('core_skills', []),
            self._format_core_skills_item
        )
        
        self._add_section_items(
            story, styles, 'skills',
            self.data.get('skills', []),
            self._format_skills_item
        )
        
        self._add_section_items(
            story, styles, 'languages',
            self.data.get('languages', []),
            self._format_language_item
        )
        
        self._add_section_items(
            story, styles, 'awards',
            self.data.get('awards', []),
            self._format_award_item
        )
        
        self._add_section_items(
            story, styles, 'certifications',
            self.data.get('certifications', []),
            self._format_certification_item
        )
        
        doc.build(story)
        
        self.logger.info(f"CV gerado com sucesso: {self.output_file}")
        print(f"✓ {self._get_text('success_generated', 'labels')}: {self.output_file}")
        return self.output_file


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Gera CV em PDF a partir de arquivo JSON (suporte multilíngue)'
    )
    parser.add_argument(
        'input',
        nargs='?',
        default=None,
        help='Arquivo JSON com dados do CV (padrão: cv_data.json)'
    )
    parser.add_argument(
        '-l', '--language',
        choices=['pt', 'en'],
        default='pt',
        help='Idioma do CV: pt (português) ou en (inglês). Padrão: pt'
    )
    parser.add_argument(
        '-o', '--output',
        help='Arquivo PDF de saída'
    )
    parser.add_argument(
        '-c', '--config',
        default='config.json',
        help='Arquivo de configuração (padrão: config.json)'
    )
    
    args = parser.parse_args()
    
    try:
        generator = CVGenerator(args.input, args.language, args.output, args.config)
        generator.generate()
    except Exception as e:
        print(f"Erro fatal: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
