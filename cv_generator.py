#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================================
# 1. IMPORTS - Required libraries
# ============================================================================

import json                           # For reading JSON files
import os                             # For operating system operations
import logging                        # For displaying log/error messages
from pathlib import Path              # For working with file paths
from xml.sax.saxutils import escape   # For escaping special characters in XML
import argparse                       # For processing command-line arguments

# ReportLab library imports (for PDF creation)
from reportlab.lib.pagesizes import A4                  # A4 page size
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # Text styles
from reportlab.lib.units import mm                      # Unit of measurement (millimeters)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer  # PDF elements
from reportlab.lib import colors                        # Colors for PDF
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY   # Text alignment
from reportlab.pdfbase import pdfmetrics              # For hyperlink support
from reportlab.lib.styles import getSampleStyleSheet   # For standard styles




# ============================================================================
# 2. MAIN CLASS - CVGenerator
# ============================================================================

class CVGenerator:
    # ========================================================================
    # 2.1 CLASS CONSTANTS - Fixed data that doesn't change
    # ========================================================================
    
    # Month abbreviations in Portuguese
    MONTHS_PT = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Month abbreviations in English
    MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    
    # ========================================================================
    # 2.2 INITIALIZATION - Class constructor
    # ========================================================================
    
    def __init__(self, json_file=None, language='pt', output_file=None, config_file='config.json'):
        """
        Initializes the CV generator.
        
        Parameters:
            json_file (str): Path to the JSON file with CV data
            language (str): Language ('pt' for Portuguese or 'en' for English)
            output_file (str): Path to the output PDF file
            config_file (str): Path to the configuration file
        """
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
        """
        Configure the logging system to display error and info messages.
        Reads the configuration file to determine the log level.
        """
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
        """
        Resolve the config.json path to an absolute path.
        """
        return Path(os.path.abspath(os.path.expanduser(str(config_file))))

    def _resolve_path(self, filepath):
        """
        Resolve relative paths from the config.json directory.
        """
        path = Path(os.path.expanduser(str(filepath)))
        if path.is_absolute():
            return path
        return self.config_dir / path
    
    def _load_config(self, config_file):
        """
        Load the configuration file (config.json).
        
        Returns:
            dict: Dictionary with configurations
            
        Exceptions:
            Exits the program if the file doesn't exist or is invalid
        """
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
        """
        Load any JSON file (CV data, styles, translations).
        
        Parameters:
            filepath (str): Path to the JSON file
            
        Returns:
            dict: Dictionary with JSON data
            
        Exceptions:
            Exits the program if the file doesn't exist or is invalid
        """
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
        """
        Validate if required data is present in the JSON file.
        Checks:
        - If 'personal_info' section exists with 'name' and 'email'
        - If 'desired_role' section exists
        
        If required data is missing, displays errors and exits the program.
        """
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
        """
        Generate the output PDF filename automatically.
        Name: Candidate_Name_Position_LANGUAGE.pdf
        Example: John_Smith_Developer_EN.pdf
        
        Returns:
            str: Full path to the output file
        """
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
        """Get translation text"""
        if section:
            return self.translations.get(self.language, {}).get(section, {}).get(key, key)
        return key
    
    def _get_localized_field(self, data, field_name, default=''):
        """
        Get a localized (translated) field from data.
        Implements smart fallback: current language → Portuguese → no suffix → default.
        
        Example:
            _get_localized_field(data, 'position')
            Searches in order:
            1. position_en (if language is 'en')
            2. position_pt (fallback to Portuguese)
            3. position (without language suffix)
            4. default (default value if everything fails)
        
        Parameters:
            data (dict): Dictionary with data
            field_name (str): Field name to search for
            default (str): Default value if not found
            
        Returns:
            str: Field value or default value
        """
        # Check if data is really a dictionary
        if not isinstance(data, dict):
            return default
        
        # 1️⃣ Try with current language (e.g., 'position_en')
        localized_field = f"{field_name}_{self.language}"
        value = data.get(localized_field, '').strip() if isinstance(data.get(localized_field), str) else ''
        
        # 2️⃣ If empty and not Portuguese, try Portuguese as fallback
        if not value and self.language != 'pt':
            value = data.get(f"{field_name}_pt", '').strip() if isinstance(data.get(f"{field_name}_pt"), str) else ''
        
        # 3️⃣ If still empty, try without language suffix
        if not value:
            value = data.get(field_name, '').strip() if isinstance(data.get(field_name), str) else ''
        
        # 4️⃣ Return found value or default
        return value if value else default
    
    
    # ========================================================================
    # 2.5 DATA FORMATTING - Functions to convert data to text
    # ========================================================================
    
    def _escape_text(self, text):
        """
        Escape special characters for safe PDF usage.
        Converts characters that could break the PDF to safe versions.
        
        Parameters:
            text (str): Text to escape
            
        Returns:
            str: Text with escaped characters
        """
        return escape(str(text), {"'": "&apos;", '"': "&quot;"})
    
    def _format_month(self, month_str):
        """
        Convert month number to abbreviation (1 -> 'Jan').
        Supports Portuguese and English.
        
        Parameters:
            month_str (str): Month number (1-12)
            
        Returns:
            str: Month abbreviation or original text if invalid
        """
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
        """
        Format a time period (start date - end date).
        
        Examples:
            "Jan 2020 - Mar 2023"
            "Jan 2020 - Present"
        
        Parameters:
            start_month (str): Start month number (1-12)
            start_year (str): Start year (2020)
            end_month (str): End month number (may be empty if current)
            end_year (str): End year (may be empty if current)
            
        Returns:
            str: Formatted period
        """
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
        """
        Create custom PDF styles.
        Define size, color, alignment, and font for each text type.
        Colors and fonts are hardcoded (don't depend on external file).
        
        Returns:
            StyleSheet1: Object with all defined styles
        """
        # ====== COLOR AND FONT DEFINITIONS (Hardcoded) ======
        FONT_NAME = 'Helvetica-Bold'
        FONT_NAME_REGULAR = 'Helvetica'
        COLOR_NAME = '#000000'           # Name (black)
        COLOR_TITLE = '#000000'          # Title (black)
        COLOR_SECTION = '#666666'        # Section titles (dark gray)
        COLOR_TEXT = '#000000'           # Body text (black)
        
        FONT_SIZE_NAME = 24              # Name font size
        FONT_SIZE_TITLE = 12             # Title font size
        FONT_SIZE_SECTION = 14           # Section title font size
        FONT_SIZE_SUBHEADING = 12        # Subheading font size
        FONT_SIZE_BODY = 10              # Body text font size
        FONT_SIZE_DATE = 9               # Date font size
        
        # Get basic styles from ReportLab
        styles = getSampleStyleSheet()
        
        # Create style for NAME (large, bold, centered)
        styles.add(ParagraphStyle(
            name='NameStyle',
            parent=styles['Heading1'],
            fontSize=FONT_SIZE_NAME,
            textColor=colors.HexColor(COLOR_NAME),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName=FONT_NAME
        ))
        
        # Create style for TITLE (desired position)
        styles.add(ParagraphStyle(
            name='TitleStyle',
            parent=styles['Normal'],
            fontSize=FONT_SIZE_TITLE,
            textColor=colors.HexColor(COLOR_TITLE),
            spaceAfter=24,
            alignment=TA_CENTER,
            fontName=FONT_NAME
        ))
        
        # Create style for SECTION TITLES (Experience, Education, etc)
        styles.add(ParagraphStyle(
            name='H2',
            parent=styles['Normal'],
            fontSize=FONT_SIZE_SECTION,
            textColor=colors.HexColor(COLOR_SECTION),
            spaceBefore=14,
            spaceAfter=6,
            fontName=FONT_NAME
        ))
        
        # Create style for SUBTITLES (Position, Company, Degree, University)
        styles.add(ParagraphStyle(
            name='H3',
            parent=styles['Normal'],
            fontSize=FONT_SIZE_SUBHEADING,
            textColor=colors.HexColor(COLOR_SECTION),
            spaceBefore=10,
            spaceAfter=4,
            leftIndent=10,
            fontName=FONT_NAME,
            keepWithNext=1
        ))

        styles.add(ParagraphStyle(
            name='H4',
            parent=styles['Normal'],
            fontSize=FONT_SIZE_SUBHEADING - 1,
            textColor=colors.HexColor(COLOR_SECTION),
            spaceAfter=2,
            leftIndent=10,
            fontName=FONT_NAME,
            keepWithNext=1
        ))
        
        # Create style for BODY TEXT (main content, justified)
        styles.add(ParagraphStyle(
            name='BodyStyle',
            parent=styles['Normal'],
            fontSize=FONT_SIZE_BODY,
            textColor=colors.HexColor(COLOR_TEXT),
            spaceAfter=2,
            leftIndent=28,
            alignment=TA_JUSTIFY,
            fontName=FONT_NAME_REGULAR
        ))

        styles.add(ParagraphStyle(
            name='ContactStyle',
            fontSize=FONT_SIZE_BODY + 1,
            parent=styles['BodyStyle'],
            alignment=TA_CENTER,
            leftIndent=0,
            fontName=FONT_NAME_REGULAR
        ))

        styles.add(ParagraphStyle(
            name='Date',
            parent=styles['Normal'],
            fontSize=FONT_SIZE_DATE,
            textColor=colors.HexColor(COLOR_TEXT),
            leftIndent=10,
            spaceAfter=2,
            fontName=FONT_NAME_REGULAR
        ))
        
        return styles
    
    
    # ========================================================================
    # 2.7 PDF ASSEMBLY - Functions to add sections
    # ========================================================================
    
    def _add_header(self, pdf_elements, styles):
        """
        Add the header to the CV document.
        Includes: Name, Desired Position, Email, Phone, Location, Social Networks.
        
        Parameters:
            pdf_elements (list): List of PDF elements
            styles (StyleSheet1): Text styles
        """
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
                phone = '+55' + phone
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
        """
        Add the professional summary section to the document.
        
        Parameters:
            pdf_elements (list): List of PDF elements
            styles (StyleSheet1): Text styles
        """
        summary_data = self.data.get('summary', {})
        summary = self._get_localized_field(summary_data, 'description').strip()
        
        # If no summary, don't add anything
        if not summary:
            return
        
        spacing = self.settings['spacing']
        section_title = self._get_text('summary', 'sections')
        
        # Add section title
        pdf_elements.append(Paragraph(section_title, styles['H2']))
        
        # Escape text and convert line breaks to <br/>
        safe_summary = self._escape_text(summary).replace('\n', '<br/>')
        pdf_elements.append(Paragraph(safe_summary, styles['BodyStyle']))
        
        # Add spacing after section
        pdf_elements.append(Spacer(1, spacing['section_bottom'] * mm))
    
    def _add_section_items(self, pdf_elements, styles, section_key, items, item_formatter):
        """
        Generic function to add sections with multiple items.
        Reuses code for Experience, Education, Skills, Languages, etc.
        
        Parameters:
            pdf_elements (list): List of PDF elements
            styles (StyleSheet1): Text styles
            section_key (str): Section key (e.g., 'experience', 'education')
            items (list): List of items to add
            item_formatter (function): Function that formats each item
        """
        # If no items, don't add anything
        if not items:
            return
        
        spacing = self.settings['spacing']
        # Get translated section title
        section_title = self._get_text(section_key, 'sections')
        
        # Add section title
        pdf_elements.append(Paragraph(section_title, styles['H2']))
        
        # For each item in section, call formatter function
        for item in items:
            item_formatter(pdf_elements, styles, item)
        
        # Add spacing after section
        pdf_elements.append(Spacer(1, spacing['item_bottom'] * mm))
    
    
    # ========================================================================
    # 2.8 ITEM FORMATTERS - Functions to format each item type
    # ========================================================================
    
    def _format_experience_item(self, pdf_elements, styles, work):
        """
        Format a professional experience item.
        
        Example output:
            [BOLD] Python Developer
            Company XYZ
            Jan 2020 - Present
            • Developed applications
            • Worked in team
        
        Parameters:
            pdf_elements (list): List of PDF elements
            styles (StyleSheet1): Text styles
            work (dict): Dictionary with work data
        """
        spacing = self.settings['spacing']
        
        # Get data
        position = self._get_localized_field(work, 'position')
        company = self._get_localized_field(work, 'company')
        period = self._format_period(work.get('start_month', ''), work.get('start_year', ''), work.get('end_month', ''), work.get('end_year', ''))
        
        # Add position in bold
        pdf_elements.append(Paragraph(f"<b>{self._escape_text(position)}</b>", styles['H3']))
        
        # Add company
        pdf_elements.append(Paragraph(f"<b>{self._escape_text(company)}</b>", styles['H4']))
        
        # Add period
        pdf_elements.append(Paragraph(f"<i>{self._escape_text(period)}</i>", styles['Date']))
        
        # Add descriptions (bullet points)
        descriptions = work.get(f'description_{self.language}') or work.get('description_pt', [])
        for description in descriptions:
            pdf_elements.append(Paragraph(f"• {self._escape_text(description)}", styles['BodyStyle']))
        
        # Add small spacing between items
        pdf_elements.append(Spacer(1, spacing['small_bottom'] * mm))
    
    def _format_education_item(self, pdf_elements, styles, education):
        """
        Format an education item (bachelor's, master's, course, etc).
        
        Example output:
            [BOLD] Bachelor's in Software Engineering
            Federal University of Brazil
            Jan 2018 - Dec 2022
            • GPA: 8.5
        
        Parameters:
            pdf_elements (list): List of PDF elements
            styles (StyleSheet1): Text styles
            education (dict): Dictionary with education data
        """
        spacing = self.settings['spacing']
        
        # Get data
        degree = self._get_localized_field(education, 'degree')
        institution = self._get_localized_field(education, 'institution')
        period = self._format_period(education.get('start_month', ''), education.get('start_year', ''), education.get('end_month', ''), education.get('end_year', '') )
        
        # Add degree in bold
        pdf_elements.append(Paragraph(f"<b>{self._escape_text(degree)}</b>", styles['H3']))
        
        # Add institution
        pdf_elements.append(Paragraph(f"<b>{self._escape_text(institution)}</b>", styles['H4']))
        
        # Add period (if exists)
        if period.strip():
            pdf_elements.append(Paragraph(f"<i>{self._escape_text(period)}</i>", styles['Date']))
        
        # Add additional notes (bullet points)
        descriptions = education.get(f'description_{self.language}') or education.get('description_pt', [])
        for note in descriptions:
            pdf_elements.append(Paragraph(f"• {self._escape_text(note)}", styles['BodyStyle']))
        
        # Add small spacing between items
        pdf_elements.append(Spacer(1, spacing['small_bottom'] * mm))
    
    def _format_core_skills_item(self, pdf_elements, styles, skill_group):
        """
        Format a core competencies item.
        
        Example output:
            [BOLD] Leadership
            • Team management
            • Communication
        
        Parameters:
            pdf_elements (list): List of PDF elements
            styles (StyleSheet1): Text styles
            skill_group (dict): Dictionary with category and skills
        """
        # Get category (e.g., "Leadership")
        category = self._get_localized_field(skill_group, 'category')
        # Get list of skills
        descriptions = skill_group.get(f'description_{self.language}') or skill_group.get('description_pt', [])
        
        # Add category in bold (if exists)
        if category:
            pdf_elements.append(Paragraph(self._escape_text(category), styles['H3']))
        
        # Add each skill with bullet point
        for item in descriptions:
            pdf_elements.append(Paragraph(f"• {self._escape_text(item)}", styles['BodyStyle']))
        
        # Small spacing
        pdf_elements.append(Spacer(1, self.settings['spacing']['minimal_bottom'] * mm))
    
    def _format_skills_item(self, pdf_elements, styles, skill_group):
        """
        Format a technical skills item.
        Items appear in one line, separated by commas.
        
        Example output:
            [BOLD] Programming Languages
            Python, JavaScript, Java, C++
        
        Parameters:
            pdf_elements (list): List of PDF elements
            styles (StyleSheet1): Text styles
            skill_group (dict): Dictionary with category and items
        """
        # Get category (e.g., "Programming Languages")
        category = self._get_localized_field(skill_group, 'category')
        # Get list of items
        items = skill_group.get('item', [])
        
        # Add category in bold (if exists)
        if category:
            pdf_elements.append(Paragraph(self._escape_text(category), styles['H3']))
        
        # If has items, join all with comma and add in one line
        if items:
            item_text = ', '.join([self._escape_text(item) for item in items])
            pdf_elements.append(Paragraph(item_text, styles['BodyStyle']))
        
        # Spacing after section
        pdf_elements.append(Spacer(1, self.settings['spacing']['item_bottom'] * mm))
    
    def _format_language_item(self, pdf_elements, styles, language):
        """
        Format a language item.
        
        Example output:
            [BOLD] Portuguese - Native
        
        Parameters:
            pdf_elements (list): List of PDF elements
            styles (StyleSheet1): Text styles
            language (dict): Dictionary with language and proficiency
        """
        # Get language
        language_name = self._get_localized_field(language, 'language')
        # Get proficiency level
        proficiency = self._get_localized_field(language, 'proficiency')
        
        # Format: [BOLD] Language - Proficiency
        language_text = f"<b>{self._escape_text(language_name)}</b> - {self._escape_text(proficiency)}"
        pdf_elements.append(Paragraph(language_text, styles['BodyStyle']))
    
    def _format_award_item(self, pdf_elements, styles, award):
        """
        Format an award or recognition item.
        
        Example output:
            [BOLD] Best Employee - Company XYZ
        
        Parameters:
            pdf_elements (list): List of PDF elements
            styles (StyleSheet1): Text styles
            award (dict): Dictionary with award title and description
        """
        # Get title and description
        award_title = self._get_localized_field(award, 'title')
        description = self._get_localized_field(award, 'description')
        
        # Format text (bold title - description)
        if award_title and description:
            award_text = f"<b>{self._escape_text(award_title)}</b> - {self._escape_text(description)}"
        else:
            # If not both, use what we have
            award_text = self._escape_text(award_title or description)
        
        # Add to PDF (if has text)
        if award_text:
            pdf_elements.append(Paragraph(award_text, styles['BodyStyle']))
    
    def _format_certification_item(self, pdf_elements, styles, certification):
        """
        Format a certification or training item.
        
        Example output:
            [BOLD] AWS Solutions Architect - Amazon Web Services (2023)
        
        Parameters:
            pdf_elements (list): List of PDF elements
            styles (StyleSheet1): Text styles
            certification (dict): Dictionary with name, issuer, and year
        """
        # Get data
        name = self._get_localized_field(certification, 'name')
        issuer = self._get_localized_field(certification, 'issuer')
        year = certification.get('year', '')
        
        # Format according to available data
        if name and issuer and year:
            # If has everything: Name - Issuer (Year)
            cert_text = f"<b>{self._escape_text(name)}</b> - {self._escape_text(issuer)} ({self._escape_text(year)})"
        elif name and issuer:
            # If no year: Name - Issuer
            cert_text = f"<b>{self._escape_text(name)}</b> - {self._escape_text(issuer)}"
        else:
            # If issuer missing: Name only
            cert_text = self._escape_text(name or issuer)
        
        # Add to PDF (if has text)
        if cert_text:
            pdf_elements.append(Paragraph(cert_text, styles['BodyStyle']))
    
    def _format_publication_item(self, pdf_elements, styles, publication):
        """
        Format a publication item.
        
        Example output:
            [BOLD] Python Automation - 2023
        
        Parameters:
            pdf_elements (list): List of PDF elements
            styles (StyleSheet1): Text styles
            publication (dict): Dictionary with title, description, and year
        """
        # Get data
        title = self._get_localized_field(publication, 'title')
        description = self._get_localized_field(publication, 'description')
        year = publication.get('year', '')
        
        # Format according to available data
        if title and year:
            # If has title and year: Title (Year)
            pub_text = f"<b>{self._escape_text(title)}</b> ({self._escape_text(year)})"
        elif title and description:
            # If has title and description: Title - Description
            pub_text = f"<b>{self._escape_text(title)}</b> - {self._escape_text(description)}"
        else:
            # If has title only
            pub_text = self._escape_text(title or description)
        
        # Add to PDF (if has text)
        if pub_text:
            pdf_elements.append(Paragraph(pub_text, styles['BodyStyle']))
    
    
    # ========================================================================
    # 2.9 SECTION MAPPER - Map section types to functions
    # ========================================================================
    
    def _get_section_formatter(self, section_type):
        """
        Return the formatter function for a section type.
        Allows easy extension with new section types.
        
        Parameters:
            section_type (str): Section type (experience, education, skills, etc)
            
        Returns:
            function: Function that formats each section item
        """
        mapper = {
            'experience': self._format_experience_item,
            'education': self._format_education_item,
            'core_skills': self._format_core_skills_item,
            'skills': self._format_skills_item,
            'languages': self._format_language_item,
            'awards': self._format_award_item,
            'certifications': self._format_certification_item,
            'publications': self._format_publication_item,
        }
        return mapper.get(section_type, None)
    
    
    # ========================================================================
    # 2.10 PDF GENERATION - Main function
    # ========================================================================
    
    def generate(self):
        """
        Main function that creates the PDF document.
        
        Steps:
        1. Create output directory
        2. Configure PDF document (size, margins)
        3. Create styles
        4. Add each section to document
        5. Save PDF file
        
        Returns:
            str: Path to generated PDF file
        """
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
    """
    Function that executes when the script is run from command line.
    Processes arguments and creates the CVGenerator.
    """
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
