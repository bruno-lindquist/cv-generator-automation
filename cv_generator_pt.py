#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Currículo em PDF com suporte multilíngue
=====================================================

Este script lê dados de um arquivo JSON e gera um currículo profissional em formato PDF.
Suporta múltiplos idiomas (Português e Inglês) em um único arquivo de dados.

Como usar:
    python cv_generator.py cv_data.json -l pt -o saida.pdf
"""

# ============================================================================
# 1. IMPORTAÇÕES - Bibliotecas necessárias
# ============================================================================

import json                           # Para ler arquivos JSON
import os                             # Para operações com o sistema operacional
import logging                        # Para exibir mensagens de log/erro
from pathlib import Path              # Para trabalhar com caminhos de arquivo
from xml.sax.saxutils import escape   # Para escapar caracteres especiais em XML
import argparse                       # Para processar argumentos de linha de comando

# Importações da biblioteca ReportLab (cria PDFs)
from reportlab.lib.pagesizes import A4                  # Tamanho de página A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # Estilos de texto
from reportlab.lib.units import mm                      # Unidade de medida (milímetros)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer  # Elementos do PDF
from reportlab.lib import colors                        # Cores para o PDF
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY   # Alinhamento de texto
from reportlab.pdfbase import pdfmetrics              # Para suporte a hiperlinks
from reportlab.lib.styles import getSampleStyleSheet   # Para estilos padrão




# ============================================================================
# 2. CLASSE PRINCIPAL - CVGenerator
# ============================================================================

class CVGenerator:
    # ========================================================================
    # 2.1 CONSTANTES DA CLASSE - Dados fixos que não mudam
    # ========================================================================
    
    # Abreviações dos meses em Português
    MONTHS_PT = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Abreviações dos meses em Inglês
    MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    
    # ========================================================================
    # 2.2 INICIALIZAÇÃO - Construtor da classe
    # ========================================================================
    
    def __init__(self, json_file=None, language='pt', output_file=None, config_file='config.json'):
        """
        Inicializa o gerador de CV.
        
        Parâmetros:
            json_file (str): Caminho do arquivo JSON com os dados do CV
            language (str): Idioma ('pt' para Português ou 'en' para Inglês)
            output_file (str): Caminho do arquivo PDF de saída
            config_file (str): Caminho do arquivo de configuração
        """
        # Resolve e carrega o arquivo de configuracao principal
        self.config_path = self._resolve_config_path(config_file)
        self.config = self._load_config(self.config_path)
        self.config_dir = self.config_path.parent
        
        # Configura o sistema de logs (mensagens de erro e info)
        self._setup_logging()
        
        # Define os arquivos e configurações
        self.language = language.lower()
        self.config_file = str(self.config_path)
        self.output_dir = self._resolve_path(self.config['files']['output_dir'])
        self.json_file = self._resolve_path(json_file or self.config['files']['data'])
        
        # Carrega os dados do CV, estilos e traduções de arquivos JSON
        self.data = self._load_json(self.json_file)
        self.settings = self._load_json(self.config['files']['styles'])
        self.translations = self._load_json(self.config['files']['translations'])
        
        # Valida se os dados obrigatórios estão presentes
        self._validate_data()
        
        # Define o nome do arquivo de saída (PDF)
        if output_file:
            self.output_file = str(self._resolve_path(output_file))
        else:
            self.output_file = self._generate_output_filename()
        
        # Log de informação
        self.logger.info(f"CVGenerator inicializado: idioma={language}, arquivo={self.json_file}")
    
    
    # ========================================================================
    # 2.3 CARREGAMENTO DE DADOS - Funções para ler arquivos
    # ========================================================================
    
    def _setup_logging(self):
        """
        Configura o sistema de logs para exibir mensagens de erro e informação.
        Lê a configuração do arquivo config.json para decidir o nível de log.
        """
        log_config = self.config.get('logging', {})
        # Define se mostra mais detalhes (INFO) ou apenas erros (WARNING)
        level = logging.INFO if log_config.get('enabled', True) else logging.WARNING
        
        # Configura como as mensagens de log aparecem
        logging.basicConfig(
            level=level,
            format='%(levelname)s: %(message)s'
        )
        # Cria o objeto logger para usar em todo o código
        self.logger = logging.getLogger(__name__)

    def _resolve_config_path(self, config_file):
        """
        Resolve o caminho do config.json para um caminho absoluto.
        """
        return Path(os.path.abspath(os.path.expanduser(str(config_file))))

    def _resolve_path(self, filepath):
        """
        Resolve caminhos relativos a partir do diretorio do config.json.
        """
        path = Path(os.path.expanduser(str(filepath)))
        if path.is_absolute():
            return path
        return self.config_dir / path
    
    def _load_config(self, config_file):
        """
        Carrega o arquivo de configuração (config.json).
        
        Retorna:
            dict: Dicionário com as configurações
            
        Exceções:
            Sai do programa se o arquivo não existir ou estiver inválido
        """
        try:
            # Abre o arquivo em modo leitura
            with open(config_file, 'r', encoding='utf-8') as arquivo:
                # Converte o conteúdo JSON em um dicionário Python
                return json.load(arquivo)
        except FileNotFoundError:
            # Arquivo não foi encontrado
            print(f"Erro: Arquivo de configuracao '{config_file}' nao encontrado")
            exit(1)  # Encerra o programa com erro
        except json.JSONDecodeError:
            # O arquivo não é um JSON válido
            print("Erro: Arquivo de configuracao JSON invalido")
            exit(1)
    
    def _load_json(self, filepath):
        """
        Carrega qualquer arquivo JSON (dados do CV, estilos, traduções).
        
        Parâmetros:
            filepath (str): Caminho do arquivo JSON
            
        Retorna:
            dict: Dicionário com os dados do JSON
            
        Exceções:
            Sai do programa se o arquivo não existir ou estiver inválido
        """
        try:
            # Obtém a codificação configurada (geralmente 'utf-8')
            encoding = self.config['defaults']['encoding']
            
            # Abre e lê o arquivo JSON
            resolved_path = self._resolve_path(filepath)
            with open(resolved_path, 'r', encoding=encoding) as arquivo:
                return json.load(arquivo)
        except FileNotFoundError:
            self.logger.error(f"Arquivo '{resolved_path}' nao encontrado")
            exit(1)
        except json.JSONDecodeError:
            self.logger.error(f"Arquivo '{resolved_path}' JSON invalido")
            exit(1)
    
    def _validate_data(self):
        """
        Valida se os dados obrigatórios estão presentes no arquivo JSON.
        Verifica:
        - Se existe a seção 'personal_info' com 'name' e 'email'
        - Se existe a seção 'desired_role'
        
        Se algum dado obrigatório está faltando, exibe os erros e encerra o programa.
        """
        erros = []  # Lista para armazenar mensagens de erro
        
        # Verifica se existe a seção de informações pessoais
        if 'personal_info' not in self.data:
            erros.append("• Falta seção 'personal_info'")
        # Se existe, verifica se tem nome e email
        elif 'name' not in self.data['personal_info'] or 'email' not in self.data['personal_info']:
            erros.append("• Falta 'personal_info.name' ou 'personal_info.email'")
        
        # Verifica se existe a seção do cargo desejado
        if 'desired_role' not in self.data:
            erros.append("• Falta seção 'desired_role'")
        
        # Se encontrou erros, exibe todos e encerra o programa
        if erros:
            self.logger.error("Arquivo cv_data.json inválido!")
            for erro in erros:
                self.logger.error(erro)
            exit(1)
        
        # Se chegou aqui, todos os dados estão OK
        self.logger.info("Dados validados com sucesso")
    
    def _generate_output_filename(self):
        """
        Gera o nome do arquivo PDF de saída automaticamente.
        Nome: Nome_do_Candidato_Cargo_IDIOMA.pdf
        Exemplo: Bruno_Silva_Desenvolvedor_EN.pdf
        
        Retorna:
            str: Caminho completo do arquivo de saída
        """
        # Obtém o diretório de saída da configuração
        output_dir = self.output_dir
        # Cria o diretório se não existir
        Path(output_dir).mkdir(exist_ok=True)
        
        # Remove espaços do nome e substitui por underscore
        nome_arquivo = self.data['personal_info']['name'].replace(' ', '_')
        
        # Obtém o cargo desejado na língua configurada
        cargo = self._get_localized_field(self.data['desired_role'], 'desired_role', 'CV')
        cargo = cargo.replace(' ', '_')
        
        # Adiciona sufixo do idioma apenas se não for português
        sufixo_idioma = f"_{self.language.upper()}" if self.language != 'pt' else ""
        
        # Retorna o caminho completo do arquivo
        return str(Path(output_dir) / f"{nome_arquivo}_{cargo}{sufixo_idioma}.pdf")
    
    
    # ========================================================================
    # 2.4 LOCALIZAÇÃO E TRADUÇÃO - Funções para trabalhar com idiomas
    # ========================================================================
    
    def _get_text(self, key, section=None):
        """Obtém texto de tradução"""
        if section:
            return self.translations.get(self.language, {}).get(section, {}).get(key, key)
        return key
    
    def _get_localized_field(self, dados, nome_campo, padrao=''):
        """
        Obtém um campo localizado (traduzido) dos dados.
        Implementa fallback inteligente: idioma atual → português → sem sufixo → padrão.
        
        Exemplo:
            _get_localized_field(dados, 'position')
            Procura em ordem:
            1. position_en (se idioma for 'en')
            2. position_pt (fallback para português)
            3. position (sem sufixo de idioma)
            4. padrao (valor padrão se tudo falhar)
        
        Parâmetros:
            dados (dict): Dicionário com os dados
            nome_campo (str): Nome do campo a procurar
            padrao (str): Valor padrão se não encontrar
            
        Retorna:
            str: Valor do campo ou valor padrão
        """
        # Verifica se dados é realmente um dicionário
        if not isinstance(dados, dict):
            return padrao
        
        # 1️⃣ Tenta com o idioma atual (ex: 'position_en')
        campo_localizado = f"{nome_campo}_{self.language}"
        valor = dados.get(campo_localizado, '').strip() if isinstance(dados.get(campo_localizado), str) else ''
        
        # 2️⃣ Se vazio e não é português, tenta português como fallback
        if not valor and self.language != 'pt':
            valor = dados.get(f"{nome_campo}_pt", '').strip() if isinstance(dados.get(f"{nome_campo}_pt"), str) else ''
        
        # 3️⃣ Se ainda vazio, tenta sem sufixo de idioma
        if not valor:
            valor = dados.get(nome_campo, '').strip() if isinstance(dados.get(nome_campo), str) else ''
        
        # 4️⃣ Retorna o valor encontrado ou o padrão
        return valor if valor else padrao
    
    
    # ========================================================================
    # 2.5 FORMATAÇÃO DE DADOS - Funções para converter dados em texto
    # ========================================================================
    
    def _escape_text(self, texto):
        """
        Escapa caracteres especiais para uso seguro em PDF.
        Converte caracteres que poderiam quebrar o PDF em versões seguras.
        
        Parâmetros:
            texto (str): Texto a escapar
            
        Retorna:
            str: Texto com caracteres escapados
        """
        return escape(str(texto), {"'": "&apos;", '"': "&quot;"})
    
    def _format_month(self, mes_str):
        """
        Converte o número do mês em abreviação (1 -> 'Jan').
        Suporta português e inglês.
        
        Parâmetros:
            mes_str (str): Número do mês (1-12)
            
        Retorna:
            str: Abreviação do mês ou o texto original se inválido
        """
        try:
            # Converte string para número
            numero_mes = int(mes_str)
            
            # Verifica se o número está entre 1 e 12
            if 1 <= numero_mes <= 12:
                # Escolhe a lista de meses conforme o idioma
                meses = self.MONTHS_PT if self.language == 'pt' else self.MONTHS_EN
                # Retorna o mês abreviado (número - 1 porque lista começa no 0)
                return meses[numero_mes - 1]
        except (ValueError, IndexError):
            # Se não conseguir converter, ignora o erro
            pass
        
        # Se não conseguiu converter, retorna o texto original
        return mes_str
    
    def _format_period(self, mes_inicio, ano_inicio, mes_fim, ano_fim):
        """
        Formata um período de tempo (data início - data fim).
        
        Exemplos:
            "Jan 2020 - Mar 2023"
            "Jan 2020 - Atual"
        
        Parâmetros:
            mes_inicio (str): Número do mês de início (1-12)
            ano_inicio (str): Ano de início (2020)
            mes_fim (str): Número do mês de fim (pode estar vazio se atual)
            ano_fim (str): Ano de fim (pode estar vazio se atual)
            
        Retorna:
            str: Período formatado
        """
        # Converte o número do mês em abreviação
        mes_inicio = self._format_month(mes_inicio)
        # Monta a data de início
        periodo = f"{mes_inicio} {ano_inicio}"
        
        # Se tem data de fim, adiciona ao período
        if mes_fim and ano_fim:
            mes_fim = self._format_month(mes_fim)
            periodo += f" - {mes_fim} {ano_fim}"
        else:
            # Se não tem data de fim, significa que ainda trabalha lá
            label_atual = self._get_text('current', 'labels')
            periodo += f" - {label_atual}"
        
        return periodo
    
    
    # ========================================================================
    # 2.6 ESTILOS - Funções para definir aparência do PDF
    # ========================================================================
    
    def _create_styles(self):
        """
        Cria os estilos personalizados para o PDF.
        Define tamanho, cor, alinhamento e fonte de cada tipo de texto.
        Cores e fontes são hardcoded (não dependem de arquivo externo).
        
        Retorna:
            StyleSheet1: Objeto com todos os estilos definidos
        """
        # ====== DEFINIÇÕES DE CORES E FONTES (Hardcoded) ======
        FONT_NAME = 'Helvetica-Bold'
        FONT_NAME_REGULAR = 'Helvetica'
        COLOR_NAME = '#000000'           # Nome (preto)
        COLOR_TITLE = '#000000'          # Título (preto)
        COLOR_SECTION = '#666666'        # Títulos de seção (cinza escuro)
        COLOR_TEXT = '#000000'           # Texto do corpo (preto)
        
        FONT_SIZE_NAME = 24              # Tamanho do nome
        FONT_SIZE_TITLE = 12             # Tamanho do título
        FONT_SIZE_SECTION = 14           # Tamanho de títulos de seção
        FONT_SIZE_SUBHEADING = 12        # Tamanho de subtítulos
        FONT_SIZE_BODY = 10              # Tamanho do texto do corpo
        FONT_SIZE_DATE = 9               # Tamanho de datas
        
        # Obtém os estilos básicos da ReportLab
        estilos = getSampleStyleSheet()
        
        # Cria estilo para o NOME (grande, negrito, centralizado)
        estilos.add(ParagraphStyle(
            name='NameStyle',
            parent=estilos['Heading1'],
            fontSize=FONT_SIZE_NAME,
            textColor=colors.HexColor(COLOR_NAME),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName=FONT_NAME
        ))
        
        # Cria estilo para o TÍTULO (cargo desejado)
        estilos.add(ParagraphStyle(
            name='TitleStyle',
            parent=estilos['Normal'],
            fontSize=FONT_SIZE_TITLE,
            textColor=colors.HexColor(COLOR_TITLE),
            spaceAfter=24,
            alignment=TA_CENTER,
            fontName=FONT_NAME
        ))
        
        # Cria estilo para TÍTULOS DE SEÇÃO (Experiência, Educação, etc)
        estilos.add(ParagraphStyle(
            name='H2',
            parent=estilos['Normal'],
            fontSize=FONT_SIZE_SECTION,
            textColor=colors.HexColor(COLOR_SECTION),
            spaceBefore=14,
            spaceAfter=6,
            fontName=FONT_NAME
        ))
        
        # Cria estilo para SUBTÍTULOS (Cargo, Empresa, Grau, Universidade)
        estilos.add(ParagraphStyle(
            name='H3',
            parent=estilos['Normal'],
            fontSize=FONT_SIZE_SUBHEADING,
            textColor=colors.HexColor(COLOR_SECTION),
            spaceBefore=10,
            spaceAfter=4,
            leftIndent=10,
            fontName=FONT_NAME,
            keepWithNext=1
        ))

        estilos.add(ParagraphStyle(
            name='H4',
            parent=estilos['Normal'],
            fontSize=FONT_SIZE_SUBHEADING - 1,
            textColor=colors.HexColor(COLOR_SECTION),
            spaceAfter=2,
            leftIndent=10,
            fontName=FONT_NAME,
            keepWithNext=1
        ))
        
        # Cria estilo para TEXTO DO CORPO (conteúdo principal, justificado)
        estilos.add(ParagraphStyle(
            name='BodyStyle',
            parent=estilos['Normal'],
            fontSize=FONT_SIZE_BODY,
            textColor=colors.HexColor(COLOR_TEXT),
            spaceAfter=2,
            leftIndent=28,
            alignment=TA_JUSTIFY,
            fontName=FONT_NAME_REGULAR
        ))

        estilos.add(ParagraphStyle(
            name='ContactStyle',
            fontSize=FONT_SIZE_BODY + 1,
            parent=estilos['BodyStyle'],
            alignment=TA_CENTER,
            leftIndent=0,
            fontName=FONT_NAME_REGULAR
        ))

        estilos.add(ParagraphStyle(
            name='Date',
            parent=estilos['Normal'],
            fontSize=FONT_SIZE_DATE,
            textColor=colors.HexColor(COLOR_TEXT),
            leftIndent=10,
            spaceAfter=2,
            fontName=FONT_NAME_REGULAR
        ))
        
        return estilos
    
    
    # ========================================================================
    # 2.7 MONTAGEM DO PDF - Funções para adicionar seções
    # ========================================================================
    
    def _add_header(self, elementos_pdf, estilos):
        """
        Adiciona o cabeçalho do CV ao documento.
        Inclui: Nome, Cargo Desejado, E-mail, Telefone, Localização, Redes Sociais.
        
        Parâmetros:
            elementos_pdf (list): Lista de elementos do PDF
            estilos (StyleSheet1): Estilos de texto
        """
        info = self.data['personal_info']
        espacamento = self.settings['spacing']
        
        # Adiciona o nome
        elementos_pdf.append(Paragraph(self._escape_text(info['name']), estilos['NameStyle']))
        
        # Adiciona o cargo desejado (se existir)
        titulo = self._get_localized_field(self.data['desired_role'], 'desired_role')
        if titulo:
            elementos_pdf.append(Paragraph(self._escape_text(titulo), estilos['TitleStyle']))
        
        # Adiciona informacoes de contato em uma unica linha
        contato_itens = []
        if info.get('phone'):
            telefone = info['phone']
            # Se o idioma e ingles, adiciona o prefixo +55 (Brasil)
            if self.language == 'en' and not telefone.startswith('+55'):
                telefone = '+55' + telefone
            contato_itens.append(telefone)

        if info.get('email'):
            contato_itens.append(info['email'])

        if info.get('location'):
            contato_itens.append(info['location'])

        if contato_itens:
            contato_texto = " | ".join(contato_itens)
            elementos_pdf.append(Paragraph(self._escape_text(contato_texto), estilos['ContactStyle']))
        
        # Adiciona redes sociais
        redes_sociais = info.get('social') or []
        if redes_sociais:
            links_sociais = []
            for item in redes_sociais:
                label = (item.get('label') or '').strip()
                url = (item.get('url') or '').strip()
                if url:
                    # Cria link clicavel usando o label como texto
                    url_escapada = self._escape_text(url)
                    label_texto = label or url
                    label_escapada = self._escape_text(label_texto)
                    links_sociais.append(
                        f'<a href="{url_escapada}" color="blue">{label_escapada}</a>'
                    )
            if links_sociais:
                texto_social = " | ".join(links_sociais)
                elementos_pdf.append(Paragraph(texto_social, estilos['ContactStyle']))
        
        # Adiciona espaçamento após o cabeçalho
        elementos_pdf.append(Spacer(1, espacamento['header_bottom'] * mm))
    
    def _add_summary(self, elementos_pdf, estilos):
        """
        Adiciona a seção de resumo profissional ao documento.
        
        Parâmetros:
            elementos_pdf (list): Lista de elementos do PDF
            estilos (StyleSheet1): Estilos de texto
        """
        dados_resumo = self.data.get('summary', {})
        resumo = self._get_localized_field(dados_resumo, 'description').strip()
        
        # Se não tiver resumo, não adiciona nada
        if not resumo:
            return
        
        espacamento = self.settings['spacing']
        titulo_secao = self._get_text('summary', 'sections')
        
        # Adiciona título da seção
        elementos_pdf.append(Paragraph(titulo_secao, estilos['H2']))
        
        # Escapa o texto e converte quebras de linha em <br/>
        resumo_seguro = self._escape_text(resumo).replace('\n', '<br/>')
        elementos_pdf.append(Paragraph(resumo_seguro, estilos['BodyStyle']))
        
        # Adiciona espaçamento após a seção
        elementos_pdf.append(Spacer(1, espacamento['section_bottom'] * mm))
    
    def _add_section_items(self, elementos_pdf, estilos, chave_secao, itens, formatador_item):
        """
        Função genérica para adicionar seções com múltiplos itens.
        Reutiliza código para Experiência, Educação, Skills, Idiomas, etc.
        
        Parâmetros:
            elementos_pdf (list): Lista de elementos do PDF
            estilos (StyleSheet1): Estilos de texto
            chave_secao (str): Chave da seção (ex: 'experience', 'education')
            itens (list): Lista de itens a adicionar
            formatador_item (function): Função que formata cada item
        """
        # Se não tem itens, não adiciona nada
        if not itens:
            return
        
        espacamento = self.settings['spacing']
        # Obtém o título da seção traduzido
        titulo_secao = self._get_text(chave_secao, 'sections')
        
        # Adiciona título da seção
        elementos_pdf.append(Paragraph(titulo_secao, estilos['H2']))
        
        # Para cada item da seção, chama a função formatadora
        for item in itens:
            formatador_item(elementos_pdf, estilos, item)
        
        # Adiciona espaçamento após a seção
        elementos_pdf.append(Spacer(1, espacamento['item_bottom'] * mm))
    
    
    # ========================================================================
    # 2.8 FORMATADORES DE ITENS - Funções para formatar cada tipo de item
    # ========================================================================
    
    def _format_experience_item(self, elementos_pdf, estilos, trabalho):
        """
        Formata um item de experiência profissional.
        
        Exemplo de saída:
            [NEGRITO] Desenvolvedor Python
            Empresa XYZ
            Jan 2020 - Atual
            • Desenvolveu aplicações
            • Trabalhou em equipe
        
        Parâmetros:
            elementos_pdf (list): Lista de elementos do PDF
            estilos (StyleSheet1): Estilos de texto
            trabalho (dict): Dicionário com dados do trabalho
        """
        espacamento = self.settings['spacing']
        
        # Obtém os dados
        cargo = self._get_localized_field(trabalho, 'position')
        empresa = self._get_localized_field(trabalho, 'company')
        periodo = self._format_period(trabalho.get('start_month', ''), trabalho.get('start_year', ''), trabalho.get('end_month', ''), trabalho.get('end_year', ''))
        
        # Adiciona cargo em negrito
        elementos_pdf.append(Paragraph(f"<b>{self._escape_text(cargo)}</b>", estilos['H3']))
        
        # Adiciona empresa
        elementos_pdf.append(Paragraph(f"<b>{self._escape_text(empresa)}</b>", estilos['H4']))
        
        # Adiciona período
        elementos_pdf.append(Paragraph(f"<i>{self._escape_text(periodo)}</i>", estilos['Date']))
        
        # Adiciona descrições (pontos/bullet points)
        descricoes = trabalho.get(f'description_{self.language}') or trabalho.get('description_pt', [])
        for descricao in descricoes:
            elementos_pdf.append(Paragraph(f"• {self._escape_text(descricao)}", estilos['BodyStyle']))
        
        # Adiciona pequeno espaçamento entre itens
        elementos_pdf.append(Spacer(1, espacamento['small_bottom'] * mm))
    
    def _format_education_item(self, elementos_pdf, estilos, educacao):
        """
        Formata um item de educação (graduação, pós, curso, etc).
        
        Exemplo de saída:
            [NEGRITO] Bacharelado em Engenharia de Software
            Universidade Federal do Brasil
            Jan 2018 - Dez 2022
            • Média: 8.5
        
        Parâmetros:
            elementos_pdf (list): Lista de elementos do PDF
            estilos (StyleSheet1): Estilos de texto
            educacao (dict): Dicionário com dados da educação
        """
        espacamento = self.settings['spacing']
        
        # Obtém os dados
        grau = self._get_localized_field(educacao, 'degree')
        instituicao = self._get_localized_field(educacao, 'institution')
        periodo = self._format_period(educacao.get('start_month', ''), educacao.get('start_year', ''), educacao.get('end_month', ''), educacao.get('end_year', '') )
        
        # Adiciona grau em negrito
        elementos_pdf.append(Paragraph(f"<b>{self._escape_text(grau)}</b>", estilos['H3']))
        
        # Adiciona instituição
        elementos_pdf.append(Paragraph(f"<b>{self._escape_text(instituicao)}</b>", estilos['H4']))
        
        # Adiciona período (se existir)
        if periodo.strip():
            elementos_pdf.append(Paragraph(f"<i>{self._escape_text(periodo)}</i>", estilos['Date']))
        
        # Adiciona notas adicionais (pontos/bullet points)
        descricoes = educacao.get(f'description_{self.language}') or educacao.get('description_pt', [])
        for nota in descricoes:
            elementos_pdf.append(Paragraph(f"• {self._escape_text(nota)}", estilos['BodyStyle']))
        
        # Adiciona pequeno espaçamento entre itens
        elementos_pdf.append(Spacer(1, espacamento['small_bottom'] * mm))
    
    def _format_core_skills_item(self, elementos_pdf, estilos, grupo_habilidade):
        """
        Formata um item de competências principais.
        
        Exemplo de saída:
            [NEGRITO] Liderança
            • Gestão de equipes
            • Comunicação
        
        Parâmetros:
            elementos_pdf (list): Lista de elementos do PDF
            estilos (StyleSheet1): Estilos de texto
            grupo_habilidade (dict): Dicionário com categoria e habilidades
        """
        # Obtém a categoria (ex: "Liderança")
        categoria = self._get_localized_field(grupo_habilidade, 'category')
        # Obtém a lista de habilidades
        descricoes = grupo_habilidade.get(f'description_{self.language}') or grupo_habilidade.get('description_pt', [])
        
        # Adiciona a categoria em negrito (se existir)
        if categoria:
            elementos_pdf.append(Paragraph(self._escape_text(categoria), estilos['H3']))
        
        # Adiciona cada habilidade com bullet point
        for item in descricoes:
            elementos_pdf.append(Paragraph(f"• {self._escape_text(item)}", estilos['BodyStyle']))
        
        # Pequeno espaçamento
        elementos_pdf.append(Spacer(1, self.settings['spacing']['minimal_bottom'] * mm))
    
    def _format_skills_item(self, elementos_pdf, estilos, grupo_skill):
        """
        Formata um item de habilidades técnicas.
        Os itens aparecem em uma linha, separados por vírgula.
        
        Exemplo de saída:
            [NEGRITO] Linguagens de Programação
            Python, JavaScript, Java, C++
        
        Parâmetros:
            elementos_pdf (list): Lista de elementos do PDF
            estilos (StyleSheet1): Estilos de texto
            grupo_skill (dict): Dicionário com categoria e itens
        """
        # Obtém a categoria (ex: "Linguagens de Programação")
        categoria = self._get_localized_field(grupo_skill, 'category')
        # Obtém a lista de itens
        itens = grupo_skill.get('item', [])
        
        # Adiciona a categoria em negrito (se existir)
        if categoria:
            elementos_pdf.append(Paragraph(self._escape_text(categoria), estilos['H3']))
        
        # Se tem itens, junta todos com vírgula e adiciona em uma linha
        if itens:
            texto_itens = ', '.join([self._escape_text(item) for item in itens])
            elementos_pdf.append(Paragraph(texto_itens, estilos['BodyStyle']))
        
        # Espaçamento após a seção
        elementos_pdf.append(Spacer(1, self.settings['spacing']['item_bottom'] * mm))
    
    def _format_language_item(self, elementos_pdf, estilos, idioma):
        """
        Formata um item de idioma.
        
        Exemplo de saída:
            [NEGRITO] Português - Nativo
        
        Parâmetros:
            elementos_pdf (list): Lista de elementos do PDF
            estilos (StyleSheet1): Estilos de texto
            idioma (dict): Dicionário com língua e proficiência
        """
        # Obtém o idioma
        nome_idioma = self._get_localized_field(idioma, 'language')
        # Obtém o nível de proficiência
        proficiencia = self._get_localized_field(idioma, 'proficiency')
        
        # Formata: [NEGRITO] Idioma - Proficiência
        texto_idioma = f"<b>{self._escape_text(nome_idioma)}</b> - {self._escape_text(proficiencia)}"
        elementos_pdf.append(Paragraph(texto_idioma, estilos['BodyStyle']))
    
    def _format_award_item(self, elementos_pdf, estilos, premio):
        """
        Formata um item de prêmio ou reconhecimento.
        
        Exemplo de saída:
            [NEGRITO] Melhor Funcionário - Empresa XYZ
        
        Parâmetros:
            elementos_pdf (list): Lista de elementos do PDF
            estilos (StyleSheet1): Estilos de texto
            premio (dict): Dicionário com título e descrição do prêmio
        """
        # Obtém título e descrição
        titulo_premio = self._get_localized_field(premio, 'title')
        descricao = self._get_localized_field(premio, 'description')
        
        # Formata o texto (título negrito - descrição)
        if titulo_premio and descricao:
            texto_premio = f"<b>{self._escape_text(titulo_premio)}</b> - {self._escape_text(descricao)}"
        else:
            # Se não tem os dois, usa o que tiver
            texto_premio = self._escape_text(titulo_premio or descricao)
        
        # Adiciona ao PDF (se tiver algum texto)
        if texto_premio:
            elementos_pdf.append(Paragraph(texto_premio, estilos['BodyStyle']))
    
    def _format_certification_item(self, elementos_pdf, estilos, certificado):
        """
        Formata um item de certificação ou treinamento.
        
        Exemplo de saída:
            [NEGRITO] AWS Solutions Architect - Amazon Web Services (2023)
        
        Parâmetros:
            elementos_pdf (list): Lista de elementos do PDF
            estilos (StyleSheet1): Estilos de texto
            certificado (dict): Dicionário com nome, emissor e ano
        """
        # Obtém os dados
        nome = self._get_localized_field(certificado, 'name')
        emissor = self._get_localized_field(certificado, 'issuer')
        ano = certificado.get('year', '')
        
        # Formata conforme os dados disponíveis
        if nome and emissor and ano:
            # Se tem tudo: Nome - Emissor (Ano)
            texto_cert = f"<b>{self._escape_text(nome)}</b> - {self._escape_text(emissor)} ({self._escape_text(ano)})"
        elif nome and emissor:
            # Se não tem ano: Nome - Emissor
            texto_cert = f"<b>{self._escape_text(nome)}</b> - {self._escape_text(emissor)}"
        else:
            # Se falta emissor: apenas Nome
            texto_cert = self._escape_text(nome or emissor)
        
        # Adiciona ao PDF (se tiver algum texto)
        if texto_cert:
            elementos_pdf.append(Paragraph(texto_cert, estilos['BodyStyle']))
    
    def _format_publication_item(self, elementos_pdf, estilos, publicacao):
        """
        Formata um item de publicação.
        
        Exemplo de saída:
            [NEGRITO] Automação em Python - 2023
        
        Parâmetros:
            elementos_pdf (list): Lista de elementos do PDF
            estilos (StyleSheet1): Estilos de texto
            publicacao (dict): Dicionário com título, descrição e ano
        """
        # Obtém os dados
        titulo = self._get_localized_field(publicacao, 'title')
        descricao = self._get_localized_field(publicacao, 'description')
        ano = publicacao.get('year', '')
        
        # Formata conforme os dados disponíveis
        if titulo and ano:
            # Se tem título e ano: Título (Ano)
            texto_pub = f"<b>{self._escape_text(titulo)}</b> ({self._escape_text(ano)})"
        elif titulo and descricao:
            # Se tem título e descrição: Título - Descrição
            texto_pub = f"<b>{self._escape_text(titulo)}</b> - {self._escape_text(descricao)}"
        else:
            # Se tem apenas título
            texto_pub = self._escape_text(titulo or descricao)
        
        # Adiciona ao PDF (se tiver algum texto)
        if texto_pub:
            elementos_pdf.append(Paragraph(texto_pub, estilos['BodyStyle']))
    
    
    # ========================================================================
    # 2.9 MAPEADOR DE SEÇÕES - Mapa tipos de seção para funções
    # ========================================================================
    
    def _get_section_formatador(self, tipo_secao):
        """
        Retorna a função formatadora para um tipo de seção.
        Permite fácil extensão com novos tipos de seção.
        
        Parâmetros:
            tipo_secao (str): Tipo da seção (experience, education, skills, etc)
            
        Retorna:
            function: Função que formata cada item da seção
        """
        mapeador = {
            'experience': self._format_experience_item,
            'education': self._format_education_item,
            'core_skills': self._format_core_skills_item,
            'skills': self._format_skills_item,
            'languages': self._format_language_item,
            'awards': self._format_award_item,
            'certifications': self._format_certification_item,
            'publications': self._format_publication_item,
        }
        return mapeador.get(tipo_secao, None)
    
    
    # ========================================================================
    # 2.10 GERAÇÃO DO PDF - Função principal
    # ========================================================================
    
    def generate(self):
        """
        Função principal que cria o documento PDF.
        
        Passos:
        1. Cria o diretório de saída
        2. Configura o documento PDF (tamanho, margens)
        3. Cria os estilos
        4. Adiciona cada seção ao documento
        5. Salva o arquivo PDF
        
        Retorna:
            str: Caminho do arquivo PDF gerado
        """
        # Cria o diretório de saída se não existir
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # Obtém configurações de margens
        config_margens = self.settings.get('margins', {})
        
        # Cria o objeto do documento PDF
        doc = SimpleDocTemplate(
            self.output_file,
            pagesize=A4,                                           # Tamanho A4
            rightMargin=config_margens.get('right', 19) * mm,    # Margem direita
            leftMargin=config_margens.get('left', 19) * mm,      # Margem esquerda
            topMargin=config_margens.get('top', 19) * mm,        # Margem superior
            bottomMargin=config_margens.get('bottom', 19) * mm   # Margem inferior
        )
        
        # Lista que armazena todos os elementos do PDF
        elementos_pdf = []
        
        # Cria os estilos personalizados
        estilos = self._create_styles()
        
        # ====== Adiciona cada seção do CV ======
        
        # Cabeçalho (nome, cargo, contato)
        self._add_header(elementos_pdf, estilos)
        
        # Resumo profissional
        self._add_summary(elementos_pdf, estilos)
        
        # ====== RENDERIZAR SEÇÕES DINÂMICAS ======
        # Tenta usar a configuração de seções (se existir)
        secoes_config = self.data.get('sections', None)
        
        if secoes_config and isinstance(secoes_config, list):
            # Se tem configuração de seções, ordena e renderiza dinamicamente
            secoes_ordenadas = sorted(
                [s for s in secoes_config if s.get('enabled', True)],
                key=lambda x: x.get('order', 999)
            )
            
            for secao in secoes_ordenadas:
                tipo_secao = secao.get('type')
                if not tipo_secao:
                    continue
                
                # Obtém a função formatadora para este tipo
                formatador = self._get_section_formatador(tipo_secao)
                if not formatador:
                    self.logger.warning(f"Tipo de seção desconhecido: {tipo_secao}")
                    continue
                
                # Obtém os dados da seção
                itens = self.data.get(tipo_secao, [])
                
                # Renderiza a seção
                self._add_section_items(
                    elementos_pdf, estilos, tipo_secao,
                    itens,
                    formatador
                )
        else:
            # FALLBACK: Se não tem configuração de seções, usa ordem padrão (compatibilidade)
            self.logger.info("Usando configuração padrão de seções (sem 'sections' no JSON)")
            
            # Seção de Experiência
            self._add_section_items(
                elementos_pdf, estilos, 'experience',
                self.data.get('experience', []),
                self._format_experience_item
            )
            
            # Seção de Educação
            self._add_section_items(
                elementos_pdf, estilos, 'education',
                self.data.get('education', []),
                self._format_education_item
            )
            
            # Seção de Competências Principais
            self._add_section_items(
                elementos_pdf, estilos, 'core_skills',
                self.data.get('core_skills', []),
                self._format_core_skills_item
            )
            
            # Seção de Habilidades Técnicas
            self._add_section_items(
                elementos_pdf, estilos, 'skills',
                self.data.get('skills', []),
                self._format_skills_item
            )
            
            # Seção de Idiomas
            self._add_section_items(
                elementos_pdf, estilos, 'languages',
                self.data.get('languages', []),
                self._format_language_item
            )
            
            # Seção de Prêmios e Reconhecimentos
            self._add_section_items(
                elementos_pdf, estilos, 'awards',
                self.data.get('awards', []),
                self._format_award_item
            )
            
            # Seção de Certificações
            self._add_section_items(
                elementos_pdf, estilos, 'certifications',
                self.data.get('certifications', []),
                self._format_certification_item
            )
        
        # ====== Construir e salvar o PDF ======
        doc.build(elementos_pdf)
        
        # Log de sucesso
        self.logger.info(f"CV gerado com sucesso: {self.output_file}")
        print(f"✓ {self._get_text('success_generated', 'labels')}: {self.output_file}")
        
        return self.output_file


# ============================================================================
# 3. FUNÇÃO PRINCIPAL - Entrada do programa
# ============================================================================

def main():
    """
    Função que executa quando o script é executado via linha de comando.
    Processa os argumentos e cria o CVGenerator.
    """
    # Cria o parser de argumentos
    parser = argparse.ArgumentParser(
        description='Gera CV em PDF a partir de arquivo JSON (suporte multilíngue)'
    )
    
    # Argumento: arquivo de entrada JSON
    parser.add_argument(
        'input',
        nargs='?',
        default=None,
        help='Arquivo JSON com dados do CV (padrão: cv_data.json)'
    )
    
    # Argumento: idioma (-l ou --language)
    parser.add_argument(
        '-l', '--language',
        choices=['pt', 'en'],
        default='pt',
        help='Idioma do CV: pt (português) ou en (inglês). Padrão: pt'
    )
    
    # Argumento: arquivo de saída (-o ou --output)
    parser.add_argument(
        '-o', '--output',
        help='Arquivo PDF de saída'
    )
    
    # Argumento: arquivo de configuração (-c ou --config)
    parser.add_argument(
        '-c', '--config',
        default=str(Path(os.path.abspath(__file__)).with_name('config.json')),
        help='Arquivo de configuração (padrão: config.json)'
    )
    
    # Lê os argumentos
    args = parser.parse_args()
    
    try:
        # Cria o gerador de CV com os argumentos
        generator = CVGenerator(args.input, args.language, args.output, args.config)
        # Gera o PDF
        generator.generate()
    except Exception as e:
        # Se tiver erro, exibe e retorna 1 (erro)
        print(f"Erro fatal: {e}")
        return 1
    
    # Se tudo correu bem, retorna 0 (sucesso)
    return 0


# ============================================================================
# 4. PONTO DE ENTRADA - Verifica se o script está sendo executado direto
# ============================================================================

if __name__ == '__main__':
    # Executa a função main e passa o código de retorno para o sistema
    exit(main())
