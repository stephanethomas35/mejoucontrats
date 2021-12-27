# -*- coding: utf-8 -*-
'''
@copyright Stéphane Thomas - 2018-2021
Générateur de contrat pour Le Mejou - https://mejou.fr
'''

#===================================================================================================
# Standard Imports
#===================================================================================================

from datetime                                       import date
from datetime                                       import timedelta
from os                                             import makedirs
from os                                             import remove
from os                                             import rename
from os                                             import system
from os.path                                        import dirname
from os.path                                        import isdir
from os.path                                        import isfile
from os.path                                        import join
from shutil                                         import make_archive
from shutil                                         import rmtree
from shutil                                         import unpack_archive
from subprocess                                     import Popen
from time                                           import sleep
import errno
import io
import re

#===================================================================================================
# Personal Imports
#===================================================================================================

from mejoucontractmanager                           import AVEL_MOR
from mejoudate                                      import MejouDate
from mejoulogger                                    import StdOutLogger
from mejoutools                                     import price_to_str


#===================================================================================================
# Types
#===================================================================================================


#===================================================================================================
# Constants
#===================================================================================================

CONTENT_XML = join('tmp', 'content.xml')


#===================================================================================================
# Implementation
#===================================================================================================

class Contract2Pdf():                                                                               #pylint: disable=too-many-instance-attributes
    '''
    Generator of PDF contract file
    '''
    def __init__(self, locataire,                                                                   #pylint: disable=too-many-arguments, too-many-locals
                       avelmor,
                       tyagathe,
                       typapy,
                       start,
                       end,
                       ratio,
                       price,
                       tax,
                       sheets,
                       towels,
                       heating,
                       cleaning,
                       cleaning_inc,
                       beds,
                       deposit,
                       house_list,
                       basedir = None):
        '''
        Contract2Pdf constructor
        @option basedir [in] (str) Directory where the
        '''
        self.logger         = StdOutLogger()

        if basedir is None:
            basedir = 'contrats'
        # end if
        self._basedir       = basedir

        self._locataire     = locataire

        self._avelmor       = avelmor
        self._tyagathe      = tyagathe
        self._typapy        = typapy

        self._start         = start
        self._end           = end

        self._ratio         = ratio
        self._price         = price
        self._tax           = tax
        self._sheets        = sheets
        self._towels        = towels

        self._heating       = heating
        self._cleaning      = cleaning
        self._cleaning_inc  = cleaning_inc
        self._beds          = beds
        self._deposit       = deposit
        self.house_list     = house_list

        self._content       = None
    # end def __init__

    def _get_template_odt(self):                                                                    #pylint: disable=no-self-use
        '''
        Get the template file name depending on selected houses
        @return (str) Template file name
        '''
        template_odt = 'TMP_Contrat.odt'
        return template_odt
    # end def _get_template_odt
    template_odt = property(_get_template_odt)

    def _get_locataire_basefile(self):
        basefile = self.template_odt
        assert basefile[-4:].lower() == '.odt'
        assert basefile[:4].upper() == 'TMP_'

        locataire = self._locataire

        for pattern in ('monsieur ', 'madame '):
            search = re.compile(re.escape(pattern), re.IGNORECASE)
            locataire = search.sub('', locataire)
        #  end for

        locataire = locataire.replace(' ', '')

        return f'{basefile[4:-4]}_{locataire}_{MejouDate.iso_date(self._start)}'
    # end def _get_locataire_basefile

    def _get_output_dir(self):
        basedir = f'{self._basedir}_{self._start.strftime("%Y")}'
        basedir = join(basedir, self._start.strftime('%m'))
        return basedir
    # end def _get_output_dir
    _output_dir = property(_get_output_dir)

    def _get_contract_odt(self):
        return join(self._output_dir,
                    f'{self._get_locataire_basefile()}.odt')
    # end def _get_contract_odt
    contract_odt = property(_get_contract_odt)

    def _get_contract_pdf(self):
        return join(self._output_dir,
                    f'{self._get_locataire_basefile()}.pdf')
    # end def _get_contract_pdf
    contract_pdf = property(_get_contract_pdf)

    @staticmethod
    def _rmtree_tmp():
        ''' Delete the 'tmp' folder and wait for real deletion '''
        while isdir('tmp'):
            try:
                rmtree('tmp')
            except OSError:
                pass
            # end try
            if isdir('tmp'):
                sleep(0.1)
            # end if
        # end while
    # end def _rmtree_tmp

    @staticmethod
    def makedirs_force(path):
        ''' Force the creation of given directory '''
        try:
            makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and isdir(path):
                pass
            else:
                raise
        # end try
    # end def makedirs_force

    def _extract_template(self):
        ''' Extract the template file into 'tmp' directory '''
        self.logger.log_dbg('extractTemplate...')

        # Delete and create tmp dir again
        self._rmtree_tmp()
        # ...wait until tmp dir is realldy deleted
        while isdir('tmp'):
            sleep(0.1)
        # end while

        self.makedirs_force('tmp')

        # Unzip templat into tmp
        template_path = join('templates', self.template_odt)
        if not isfile(template_path):
            self.logger.log_error(f'Le template {self.template_odt} n\'existe pas !')
            return
        # end if

        unpack_archive(filename     = template_path,
                       extract_dir  = 'tmp',
                       format       = 'zip')
    # end def _extract_template

    def _get_house_list(self):
        result = ', '.join(self.house_list)
        return result.replace(' + ', ', ')
    # end def _get_house_list

    def _get_loft_list(self):
        loft_list = [h for h in self.house_list if h != AVEL_MOR]
        result = ', '.join(loft_list)
        return result.replace(' + ', ', ')
    # end def _get_house_list

    def _replace_fields(self):
        ''' Replace fields from ODT file '''
        self.logger.log_dbg('replaceFields...')

        #pylint: disable=line-too-long
        sub_list = (
                    ('__locataire__',   self._locataire),
                    ('__houselist__',   self._get_house_list()),
                    ('__loftlist__',    self._get_loft_list()),

                    ('__validity__',    MejouDate.full_date(date.today() + timedelta(7))),
                    ('__start__',       MejouDate.full_date(self._start)),
                    ('__end__',         MejouDate.full_date(self._end)),

                    ('__ratio__',       f'{self._ratio}'),
                    ('__price__',       price_to_str(self._price)),
                    ('__tax__',         price_to_str(self._tax)),
                    ('__taxyear__',     '2021'),
                    ('__rest__',        price_to_str(self._price*(1-self._ratio/100))),
                    ('__arrhes__',      price_to_str(self._price*self._ratio/100)),
                    ('__beds__',        f'{self._beds}'),

                    ('__deposit__',     price_to_str(self._deposit)),
                    ('__elec__',        '0,20'),
                    ('__water__',       '3'),
                    ('__sheets__',      price_to_str(self._sheets)),
                    ('__towels__',      price_to_str(self._towels)),
                    ('__heatings__',    price_to_str(self._heating)),
                  )
        #pylint: enable=line-too-long

        for tag, value in sub_list:
            self._content = re.sub(tag, value, self._content)
        # end for

        # Fill __menage__
        if self._cleaning_inc:
            cleaning = '(ménage inclus)'
        else:
            cleaning = f'{price_to_str(self._cleaning)} Euros'
        # end if
        self._content = re.sub('__cleaning__', cleaning, self._content)

        if self._avelmor:
            # Suppress the labels <!-- __avelmorstart__ --> and <!-- __avelmorend__ -->
            self._content = re.sub('<!-- __avelmorstart__ -->', '', self._content)
            self._content = re.sub('<!-- __avelmorend__ -->', '', self._content)
            self._content = re.sub('<!-- __avelmorstart1__ -->', '', self._content)
            self._content = re.sub('<!-- __avelmorend1__ -->', '', self._content)
        else:
            # Suppress the whole block between <!-- __avelmorstart__ --> and <!-- __avelmorend__ -->
            self._content = re.sub('<!-- __avelmorstart__ -->.*<!-- __avelmorend__ -->',
                                   '',
                                   self._content,
                                   flags = re.S)
            self._content = re.sub('<!-- __avelmorstart1__ -->.*<!-- __avelmorend1__ -->',
                                   '',
                                   self._content,
                                   flags = re.S)
        # end if

        if self._tyagathe or self._typapy:
            # Suppress the labels <!-- __loftsstart__ --> and <!-- __loftsend__ -->
            self._content = re.sub('<!-- __loftsstart__ -->', '', self._content)
            self._content = re.sub('<!-- __loftsend__ -->', '', self._content)
        else:
            # Suppress the whole block between <!-- __loftsstart__ --> and <!-- __loftsend__ -->
            self._content = re.sub('<!-- __loftsstart__ -->.*<!-- __loftsend__ -->',
                                   '',
                                   self._content,
                                   flags = re.S)
        # end if

        offset = self._content.find('__')
        if offset != -1:
            raise ValueError(f'Il reste la balise {self._content[offset:offset+15]}...')
        # end if
    # end def _replace_fields

    def _load_content(self):
        ''' Load content file (part of ODT file) '''
        self.logger.log_dbg('loadContent...')

        # Read UTF-8 text
        with io.open(CONTENT_XML, mode='r', encoding='utf8') as xml_file:
            self._content = xml_file.read()
        # end with
    # end def _load_content

    def _save_content(self):
        ''' Save the content (part of ODT file) '''
        self.logger.log_dbg('saveContent...')

        remove(CONTENT_XML)

        while isfile(CONTENT_XML):
            sleep(0.1)
        # end while

        # Save UTF-8 text
        with io.open(CONTENT_XML, mode='w', encoding='utf8') as content_file:
            content_file.write(self._content)
        # end with
    # end def _save_content

    def _save_odt(self):
        ''' Generate the ODT file '''
        self.logger.log_dbg('saveOdt...')

        # Unzip tmp file odt file
        make_archive(base_name = self.contract_odt,
                     format    = 'zip',
                     root_dir  = 'tmp')
        if isfile(self.contract_odt):
            remove(self.contract_odt)
        # end if
        rename(self.contract_odt + '.zip',
               self.contract_odt)
    # end def _save_odt

    def _delete_pdf_file(self):
        ''' Delete the PDF file if it exists (kill process of Foxit Reader if needed) '''
        pdf_file = self.contract_pdf
        if isfile(pdf_file):
            try:
                remove(pdf_file)
            except PermissionError:
                self._kill_foxit_reader()
                remove(pdf_file)
            # end try
        # end if

        while isfile(pdf_file):
            self.logger.log_dbg(f'Attente suppression de {pdf_file}...')
            sleep(0.5)
        # end while
    # end def _delete_pdf_file

    @staticmethod
    def _get_odt2pdf_exe_args(odt_file, dest_dir):
        prog_path    = join('C:\\', 'Program Files', 'LibreOffice', 'program', 'soffice.exe')
        if not isfile(prog_path):
            raise ValueError(f'Program does not exist: {prog_path}')
        # end if
        if not isfile(odt_file):
            raise ValueError(f'ODT file does not exist: {odt_file}')
        # end if
        args        = [prog_path,
                       '--headless',
                       '--convert-to',
                       'pdf',
                       '--outdir',
                       dest_dir,
                       odt_file]
        return args
    # end def _get_odt2pdf_exe_args

    def _get_odt2pdf_args(self):
        '''
        Generate the command line arguments of LibreOffice to generate the PDF file
        @return (list) List of arguments
        '''
        odt_file     = self.contract_odt
        dest_dir     = dirname(self.contract_odt)

        return self._get_odt2pdf_exe_args(odt_file, dest_dir)
    # end def _get_odt2pdf_args

    def _call_libre_office(self):
        '''
        Call LibreOffice to generate the PDF file
        @return (str) Path to PDF File, or ODT file if not PDF File was created
        '''
        if not isfile(self.contract_odt):
            raise RuntimeError(f'Le fichier {self.contract_odt} n\'existe pas')
        # end while

        args = self._get_odt2pdf_args()

        shell = False
        if shell:
            args = ' '.join(args)
        else:
            if not isfile(args[0]):
                raise RuntimeError(f'Le programme n\'existe pas: {args[0]}')
            # end while
        # end if

        self.logger.log_dbg(f'Popen args  = {args}')
        self.logger.log_dbg(f'Popen shell = {shell}')

        Popen(args   = args,
              shell  = shell)

        for _ in range(7):
            self.logger.log_dbg(f'Attente de création de {self.contract_pdf}...')
            if isfile(self.contract_pdf):
                file_path = self.contract_pdf
                break
            # end if
            sleep(2)
        else:
            self.logger.log_error(f'Impossible de créer le fichier PDF {self.contract_pdf}')
            file_path = self.contract_odt
        # end while

        return file_path
    # end def _call_libre_office

    def _convert_to_pdf(self):
        '''
        Convert the ODT file into PDF
        @return (str) Path to PDF File, or ODT file if not PDF File was created
        '''
        self.logger.log_dbg('_convert_to_pdf...')

        # Delete PDF File if it already exists
        self._delete_pdf_file()

        return self._call_libre_office()
    # end def _convert_to_pdf

    @staticmethod
    def _kill_foxit_reader():
        ''' Kill the process of Foxit Reader '''
        system('taskkill /im Foxit*')
        sleep(2)
    # end def _kill_foxit_reader

    def create_pdf(self):
        '''
        Generate the PDF contract file
        @return (str) Path to PDF File, or ODT file if not PDF File was created
        '''
        self.logger.log('Création du fichier LibreOffice')
        self._extract_template()
        self._load_content()
        self._replace_fields()
        self._save_content()
        self._save_odt()

        self.logger.log('Conversion du fichier en PDF')
        file_path = self._convert_to_pdf()
        self._rmtree_tmp()

        self.logger.log(f'Fichier {file_path} créé')

        return file_path
    # end def create_pdf
# end class Contract2Pdf


#===================================================================================================
# Main
#===================================================================================================


#===================================================================================================
# End
#===================================================================================================
