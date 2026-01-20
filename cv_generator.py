#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CV Generator - Supported formatting tags in text fields:
# <b>bold text</b> for bold
# <i>italic text</i> for italic
# <u>underlined text</u> for underlined
# Tags can be mixed: <b>Bold and <i>italic</i></b>

import json                           # For reading JSON files
import os                             # For operating system operations
import logging                        # For displaying log/error messages
from pathlib import Path              # For working with file paths
from xml.sax.saxutils import escape   # For escaping special characters in XML
import argparse                       # For processing command-line arguments

# ReportLab library imports (for PDF creation)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# ============================================================================
# 2. MAIN CLASS - CV Generator
# ============================================================================

class CVGenerator:
    # ========================================================================
    # 2.1 CLASS CONSTANTS - Fixed data that doesn't change
    # ========================================================================
    
    # Month abbreviations in Portuguese
    MONTHS_PT = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Month abbreviations in English
    MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Tag markers for protected formatting
    TAG_MARKERS = {
        '<b>': '___BOLD_START___', '</b>': '___BOLD_END___',
        '<i>': '___ITALIC_START___', '</i>': '___ITALIC_END___',
        '<u>': '___UNDERLINE_START___', '</u>': '___UNDERLINE_END___'
    }
    
    
    # ========================================================================
    # 2.2 INITIALIZATION - Class constructor
    # ========================================================================
    
    def __init__(self, json_file=None, language='pt', output_file=None, config_file='config.json'):
        # Resolve and load the main configuration file
        self.config_path = self._resolve_config_path(config_file)
        self.config = self._load_config(self.config_path)
        self.config_dir = self.config_path.parent
        
        # Configure the logging system (error and info messages)
        self._setup_logging()
        
        # Define files and configurations
        self.language = language.lower()
        self.config_file = str(self.config_path)
        self.output_dir = self._resolve_path(self.config['files']['output_dir'])
        self.json_file = self._resolve_path(json_file or self.config['files']['data'])
        
        # Load CV data, styles, and translations from JSON files
        self.data = self._load_json(self.json_file)
        self.settings = self._load_json(self.config['files']['styles'])
        self.translations = self._load_json(self.config['files']['translations'])
        
        # Validate if required data is present
        self._validate_data()
        
        # Define the output PDF filename
        if output_file:
            self.output_file = str(self._resolve_path(output_file))
        else:
            self.output_file = self._generate_output_filename()
        
        # Log information
        self.logger.info(f"CVGenerator initialized: language={language}, file={self.json_file}")
    
    
    # ========================================================================
    # 2.3 DATA LOADING - Functions for reading files
    # ========================================================================
    
    def _setup_logging(self):
        log_config = self.config.get('logging', {})
        # Define whether to show more details (INFO) or only errors (WARNING)
        level = logging.INFO if log_config.get('enabled', True) else logging.WARNING
        
        # Configure how log messages appear
        logging.basicConfig(
            level=level,
            format='%(levelname)s: %(message)s'
        )
        # Create the logger object for use throughout the code
        self.logger = logging.getLogger(__name__)

    def _resolve_config_path(self, config_file):
        return Path(os.path.abspath(os.path.expanduser(str(config_file))))

    def _resolve_path(self, filepath):
        path = Path(os.path.expanduser(str(filepath)))
        if path.is_absolute():
            return path
        return self.config_dir / path
    
    def _load_config(self, config_file):
        try:
            # Open the file in read mode
            with open(config_file, 'r', encoding='utf-8') as file:
                # Convert JSON content to a Python dictionary
                return json.load(file)
        except FileNotFoundError:
            # File was not found
            print(f"Error: Configuration file '{config_file}' not found")
            exit(1)  # Exit the program with error
        except json.JSONDecodeError:
            # The file is not valid JSON
            print("Error: Configuration file JSON is invalid")
            exit(1)
    
    def _load_json(self, filepath):
        try:
            # Get the encoding configured (usually 'utf-8')
            encoding = self.config['defaults']['encoding']
            
            # Open and read the JSON file
            resolved_path = self._resolve_path(filepath)
            with open(resolved_path, 'r', encoding=encoding) as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.error(f"File '{resolved_path}' not found")
            exit(1)
        except json.JSONDecodeError:
            self.logger.error(f"File '{resolved_path}' JSON is invalid")
            exit(1)
    
    def _validate_data(self):
        errors = []  # List to store error messages
        
        # Check if personal information section exists
        if 'personal_info' not in self.data:
            errors.append("• Missing 'personal_info' section")
        # If it exists, check if it has name and email
        elif 'name' not in self.data['personal_info'] or 'email' not in self.data['personal_info']:
            errors.append("• Missing 'personal_info.name' or 'personal_info.email'")
        
        # Check if desired role section exists
        if 'desired_role' not in self.data:
            errors.append("• Missing 'desired_role' section")
        
        # If errors were found, display all and exit the program
        if errors:
            self.logger.error("Invalid cv_data.json file!")
            for error in errors:
                self.logger.error(error)
            exit(1)
        
        # If we got here, all data is OK
        self.logger.info("Data validated successfully")
    
    def _generate_output_filename(self):
        # Get the output directory from configuration
        output_dir = self.output_dir
        # Create the directory if it doesn't exist
        Path(output_dir).mkdir(exist_ok=True)
        
        # Remove spaces from name and replace with underscore
        filename = self.data['personal_info']['name'].replace(' ', '_')
        
        # Get the desired position in the configured language
        position = self._get_localized_field(self.data['desired_role'], 'desired_role', 'CV')
        position = position.replace(' ', '_')
        
        # Add language suffix only if not Portuguese
        language_suffix = f"_{self.language.upper()}" if self.language != 'pt' else ""
        
        # Return the full path to the file
        return str(Path(output_dir) / f"{filename}_{position}{language_suffix}.pdf")
    
    
    # ========================================================================
    # 2.4 LOCALIZATION AND TRANSLATION - Functions for working with languages
    # ========================================================================
    
    def _get_text(self, key, section=None):
        if section:
            return self.translations.get(self.language, {}).get(section, {}).get(key, key)
        return key
    
    def _get_localized_field(self, data, field_name, default=''):
        if not isinstance(data, dict):
            return default
        value = (data.get(f"{field_name}_{self.language}") or 
                (data.get(f"{field_name}_pt") if self.language != 'pt' else None) or 
                data.get(field_name) or '')
        return (value.strip() if isinstance(value, str) else str(value)).strip() or default
    
    
    # ========================================================================
    # 2.5 DATA FORMATTING - Functions to convert data to text
    # ========================================================================
    
    def _escape_text(self, text):
        text_str = str(text)
        protected = text_str
        for tag, marker in self.TAG_MARKERS.items():
            protected = protected.replace(tag, marker)
        
        escaped = escape(protected, {"'": "&apos;", '"': "&quot;"})
        
        reverse_markers = {v: k for k, v in self.TAG_MARKERS.items()}
        for marker, tag in reverse_markers.items():
            escaped = escaped.replace(marker, tag)
        return escaped
    
    def _process_tags(self, text):
        safe_text = self._escape_text(text)
        safe_text = safe_text.replace('\n', '<br/>')
        return safe_text
    
    def _format_month(self, month_str):
        try:
            # Convert string to number
            month_number = int(month_str)
            
            # Check if the number is between 1 and 12
            if 1 <= month_number <= 12:
                # Choose the month list according to language
                months = self.MONTHS_PT if self.language == 'pt' else self.MONTHS_EN
                # Return the abbreviated month (number - 1 because list starts at 0)
                return months[month_number - 1]
        except (ValueError, IndexError):
            # If conversion fails, ignore the error
            pass
        
        # If couldn't convert, return original text
        return month_str
    
    def _format_period(self, start_month, start_year, end_month, end_year):
        # Convert month number to abbreviation
        start_month = self._format_month(start_month)
        # Build the start date
        period = f"{start_month} {start_year}"
        
        # If there's an end date, add it to the period
        if end_month and end_year:
            end_month = self._format_month(end_month)
            period += f" - {end_month} {end_year}"
        else:
            # If there's no end date, means still working there
            current_label = self._get_text('current', 'labels')
            period += f" - {current_label}"
        
        return period
    
    
    # ========================================================================
    # 2.6 STYLES - Functions to define PDF appearance
    # ========================================================================
    
    def _create_styles(self):
        
        # Get basic styles from ReportLab
        styles = getSampleStyleSheet()
        
        # Create style for NAME (large, bold, centered)
        styles.add(ParagraphStyle(
            name='NameStyle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#000000'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Create style for TITLE (desired position)
        styles.add(ParagraphStyle(
            name='TitleStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#000000'),
            spaceAfter=24,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Create style for SECTION TITLES (Experience, Education, etc)
        styles.add(ParagraphStyle(
            name='H2',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#888888'),
            spaceBefore=14,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Create style for SUBTITLES (Position, Company, Degree, University)
        styles.add(ParagraphStyle(
            name='H3',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#000000'),
            spaceBefore=10,
            spaceAfter=4,
            leftIndent=10,
            fontName='Helvetica-Bold',
            keepWithNext=1
        ))

        styles.add(ParagraphStyle(
            name='H4',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#000000'),
            spaceAfter=2,
            leftIndent=10,
            fontName='Helvetica-Bold',
            keepWithNext=1
        ))
        
        # Create style for BODY TEXT (main content, justified)
        styles.add(ParagraphStyle(
            name='BodyStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#000000'),
            spaceAfter=2,
            leftIndent=28,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))

        styles.add(ParagraphStyle(
            name='ContactStyle',
            fontSize=11,
            parent=styles['BodyStyle'],
            alignment=TA_CENTER,
            leftIndent=0,
            fontName='Helvetica'
        ))

        styles.add(ParagraphStyle(
            name='Date',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#000000'),
            leftIndent=10,
            spaceAfter=2,
            fontName='Helvetica'
        ))
        
        return styles
    
    
    # ========================================================================
    # 2.7 PDF ASSEMBLY - Functions to add sections
    # ========================================================================
    
    def _add_header(self, pdf_elements, styles):
        info = self.data['personal_info']
        spacing = self.settings['spacing']
        
        # Add the name
        pdf_elements.append(Paragraph(self._escape_text(info['name']), styles['NameStyle']))
        
        # Add desired position (if exists)
        title = self._get_localized_field(self.data['desired_role'], 'desired_role')
        if title:
            pdf_elements.append(Paragraph(self._escape_text(title), styles['TitleStyle']))
        
        # Add contact information in one line
        contact_items = []
        if info.get('phone'):
            phone = info['phone']
            # If language is English, add +55 prefix (Brazil)
            if self.language == 'en' and not phone.startswith('+55'):
                phone = '+55 ' + phone
            contact_items.append(phone)

        if info.get('email'):
            contact_items.append(info['email'])

        if info.get('location'):
            contact_items.append(info['location'])

        if contact_items:
            contact_text = " | ".join(contact_items)
            pdf_elements.append(Paragraph(self._escape_text(contact_text), styles['ContactStyle']))
        
        # Add social networks
        social_networks = info.get('social') or []
        if social_networks:
            social_links = []
            for item in social_networks:
                label = (item.get('label') or '').strip()
                url = (item.get('url') or '').strip()
                if url:
                    # Create clickable link using label as text
                    escaped_url = self._escape_text(url)
                    label_text = label or url
                    escaped_label = self._escape_text(label_text)
                    social_links.append(
                        f'<a href="{escaped_url}" color="blue">{escaped_label}</a>'
                    )
            if social_links:
                social_text = " | ".join(social_links)
                pdf_elements.append(Paragraph(social_text, styles['ContactStyle']))
        
        # Add spacing after header
        pdf_elements.append(Spacer(1, spacing['header_bottom'] * mm))
    
    def _add_summary(self, pdf_elements, styles):
        summary = self._get_localized_field(self.data.get('summary', {}), 'description').strip()
        if not summary:
            return
        
        pdf_elements.append(Paragraph(self._get_text('summary', 'sections'), styles['H2']))
        pdf_elements.append(Paragraph(self._process_tags(summary), styles['BodyStyle']))
        pdf_elements.append(Spacer(1, self.settings['spacing']['section_bottom'] * mm))
    
    def _add_section_items(self, pdf_elements, styles, section_key, items, item_formatter):
        if not items:
            return
        pdf_elements.append(Paragraph(self._get_text(section_key, 'sections'), styles['H2']))
        for item in items:
            item_formatter(pdf_elements, styles, item)
        pdf_elements.append(Spacer(1, self.settings['spacing']['item_bottom'] * mm))
    
    
    # ========================================================================
    # 2.8 ITEM FORMATTERS - Functions to format each item type
    # ========================================================================
    
    def _format_experience_item(self, pdf_elements, styles, work):
        position = self._get_localized_field(work, 'position')
        company = self._get_localized_field(work, 'company')
        period = self._format_period(work.get('start_month', ''), work.get('start_year', ''), 
                                    work.get('end_month', ''), work.get('end_year', ''))
        
        pdf_elements.append(Paragraph(f"<b>{self._escape_text(position)}</b>", styles['H3']))
        pdf_elements.append(Paragraph(f"<b>{self._escape_text(company)}</b>", styles['H4']))
        pdf_elements.append(Paragraph(f"<i>{self._escape_text(period)}</i>", styles['Date']))
        
        descriptions = work.get(f'description_{self.language}') or work.get('description_pt', [])
        for desc in descriptions:
            pdf_elements.append(Paragraph(f"• {self._escape_text(desc)}", styles['BodyStyle']))
        pdf_elements.append(Spacer(1, self.settings['spacing']['small_bottom'] * mm))
    
    def _format_education_item(self, pdf_elements, styles, education):
        degree = self._get_localized_field(education, 'degree')
        institution = self._get_localized_field(education, 'institution')
        period = self._format_period(education.get('start_month', ''), education.get('start_year', ''), 
                                    education.get('end_month', ''), education.get('end_year', ''))
        
        pdf_elements.append(Paragraph(f"<b>{self._escape_text(degree)}</b>", styles['H3']))
        pdf_elements.append(Paragraph(f"<b>{self._escape_text(institution)}</b>", styles['H4']))
        if period.strip():
            pdf_elements.append(Paragraph(f"<i>{self._escape_text(period)}</i>", styles['Date']))
        
        descriptions = education.get(f'description_{self.language}') or education.get('description_pt', [])
        for note in descriptions:
            pdf_elements.append(Paragraph(f"• {self._escape_text(note)}", styles['BodyStyle']))
        pdf_elements.append(Spacer(1, self.settings['spacing']['small_bottom'] * mm))
    
    def _format_core_skills_item(self, pdf_elements, styles, skill_group):
        category = self._get_localized_field(skill_group, 'category')
        descriptions = skill_group.get(f'description_{self.language}') or skill_group.get('description_pt', [])
        
        if category:
            pdf_elements.append(Paragraph(self._escape_text(category), styles['H3']))
        for item in descriptions:
            pdf_elements.append(Paragraph(f"• {self._escape_text(item)}", styles['BodyStyle']))
        pdf_elements.append(Spacer(1, self.settings['spacing']['minimal_bottom'] * mm))
    
    def _format_skills_item(self, pdf_elements, styles, skill_group):
        category = self._get_localized_field(skill_group, 'category')
        items = skill_group.get('item', [])
        
        if category:
            pdf_elements.append(Paragraph(self._escape_text(category), styles['H3']))
        if items:
            item_text = ', '.join([self._escape_text(item) for item in items])
            pdf_elements.append(Paragraph(item_text, styles['BodyStyle']))
        pdf_elements.append(Spacer(1, self.settings['spacing']['item_bottom'] * mm))
    
    def _format_language_item(self, pdf_elements, styles, language):
        language_name = self._get_localized_field(language, 'language')
        proficiency = self._get_localized_field(language, 'proficiency')
        text = f"<b>{self._escape_text(language_name)}</b> - {self._escape_text(proficiency)}"
        pdf_elements.append(Paragraph(text, styles['BodyStyle']))
    
    def _format_award_item(self, pdf_elements, styles, award):
        title = self._get_localized_field(award, 'title')
        desc = self._get_localized_field(award, 'description')
        text = (f"<b>{self._escape_text(title)}</b> - {self._escape_text(desc)}" 
                if title and desc else self._escape_text(title or desc))
        if text:
            pdf_elements.append(Paragraph(text, styles['BodyStyle']))
    
    def _format_certification_item(self, pdf_elements, styles, cert):
        name = self._get_localized_field(cert, 'name')
        issuer = self._get_localized_field(cert, 'issuer')
        year = cert.get('year', '')
        
        if name and issuer and year:
            text = f"<b>{self._escape_text(name)}</b> - {self._escape_text(issuer)} ({self._escape_text(year)})"
        elif name and issuer:
            text = f"<b>{self._escape_text(name)}</b> - {self._escape_text(issuer)}"
        else:
            text = self._escape_text(name or issuer)
        
        if text:
            pdf_elements.append(Paragraph(text, styles['BodyStyle']))
    
    # ========================================================================
    # 2.9 SECTION MAPPER - Map section types to functions
    # ========================================================================
    
    def _get_section_formatter(self, section_type):
        mapper = {
            'experience': self._format_experience_item,
            'education': self._format_education_item,
            'core_skills': self._format_core_skills_item,
            'skills': self._format_skills_item,
            'languages': self._format_language_item,
            'awards': self._format_award_item,
            'certifications': self._format_certification_item,
        }
        return mapper.get(section_type, None)
    
    
    # ========================================================================
    # 2.10 PDF GENERATION - Main function
    # ========================================================================
    
    def generate(self):
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # Get margin configurations
        margin_config = self.settings.get('margins', {})
        
        # Create PDF document object
        doc = SimpleDocTemplate(
            self.output_file,
            pagesize=A4,                                           # A4 size
            rightMargin=margin_config.get('right', 19) * mm,    # Right margin
            leftMargin=margin_config.get('left', 19) * mm,      # Left margin
            topMargin=margin_config.get('top', 19) * mm,        # Top margin
            bottomMargin=margin_config.get('bottom', 19) * mm   # Bottom margin
        )
        
        # List that stores all PDF elements
        pdf_elements = []
        
        # Create custom styles
        styles = self._create_styles()
        
        # ====== Add each CV section ======
        
        # Header (name, position, contact)
        self._add_header(pdf_elements, styles)
        
        # Professional summary
        self._add_summary(pdf_elements, styles)
        
        # ====== RENDER DYNAMIC SECTIONS ======
        # Try to use section configuration (if it exists)
        sections_config = self.data.get('sections', None)
        
        if sections_config and isinstance(sections_config, list):
            # If has section configuration, sort and render dynamically
            sorted_sections = sorted(
                [s for s in sections_config if s.get('enabled', True)],
                key=lambda x: x.get('order', 999)
            )
            
            for section in sorted_sections:
                section_type = section.get('type')
                if not section_type:
                    continue
                
                # Get formatter function for this type
                formatter = self._get_section_formatter(section_type)
                if not formatter:
                    self.logger.warning(f"Unknown section type: {section_type}")
                    continue
                
                # Get section data
                items = self.data.get(section_type, [])
                
                # Render section
                self._add_section_items(
                    pdf_elements, styles, section_type,
                    items,
                    formatter
                )
        else:
            # FALLBACK: If no section configuration, use default order (compatibility)
            self.logger.info("Using default section configuration (no 'sections' in JSON)")
            
            # Experience section
            self._add_section_items(
                pdf_elements, styles, 'experience',
                self.data.get('experience', []),
                self._format_experience_item
            )
            
            # Education section
            self._add_section_items(
                pdf_elements, styles, 'education',
                self.data.get('education', []),
                self._format_education_item
            )
            
            # Core skills section
            self._add_section_items(
                pdf_elements, styles, 'core_skills',
                self.data.get('core_skills', []),
                self._format_core_skills_item
            )
            
            # Technical skills section
            self._add_section_items(
                pdf_elements, styles, 'skills',
                self.data.get('skills', []),
                self._format_skills_item
            )
            
            # Languages section
            self._add_section_items(
                pdf_elements, styles, 'languages',
                self.data.get('languages', []),
                self._format_language_item
            )
            
            # Awards and recognition section
            self._add_section_items(
                pdf_elements, styles, 'awards',
                self.data.get('awards', []),
                self._format_award_item
            )
            
            # Certifications section
            self._add_section_items(
                pdf_elements, styles, 'certifications',
                self.data.get('certifications', []),
                self._format_certification_item
            )
        
        # ====== Build and save PDF ======
        doc.build(pdf_elements)
        
        # Success log
        self.logger.info(f"CV generated successfully: {self.output_file}")
        print(f"✓ {self._get_text('success_generated', 'labels')}: {self.output_file}")
        
        return self.output_file


# ============================================================================
# 3. MAIN FUNCTION - Program entry
# ============================================================================

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='Generate CV in PDF from JSON file (with multilingual support)'
    )
    
    # Argument: input JSON file
    parser.add_argument(
        'input',
        nargs='?',
        default=None,
        help='JSON file with CV data (default: cv_data.json)'
    )
    
    # Argument: language (-l or --language)
    parser.add_argument(
        '-l', '--language',
        choices=['pt', 'en'],
        default='pt',
        help='CV language: pt (Portuguese) or en (English). Default: pt'
    )
    
    # Argument: output file (-o or --output)
    parser.add_argument(
        '-o', '--output',
        help='Output PDF file'
    )
    
    # Argument: configuration file (-c or --config)
    parser.add_argument(
        '-c', '--config',
        default=str(Path(os.path.abspath(__file__)).with_name('config.json')),
        help='Configuration file (default: config.json)'
    )
    
    # Read arguments
    args = parser.parse_args()
    
    try:
        # Create CV generator with arguments
        generator = CVGenerator(args.input, args.language, args.output, args.config)
        # Generate PDF
        generator.generate()
    except Exception as e:
        # If error, display and return 1 (error)
        print(f"Fatal error: {e}")
        return 1
    
    # If everything went well, return 0 (success)
    return 0


# ============================================================================
# 4. ENTRY POINT - Check if script is being executed directly
# ============================================================================

if __name__ == '__main__':
    # Execute main function and pass return code to system
    exit(main())
