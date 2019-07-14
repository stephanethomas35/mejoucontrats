# -*- coding: utf-8 -*-
'''
@copyright Stéphane Thomas - 2018
Générateur de contrat pour Le Mejou - http://mejou.fr
'''

# @TODO: supprimer Avel Mor des contrats sans Avel Mor
# @TODO: supprimer les lofts des contrats sans aucun loft

#===================================================================================================
# Imports
#===================================================================================================

from copy                                           import copy
from datetime                                       import date
from datetime                                       import timedelta
from datetools                                      import DateTools
from logger                                         import AbstractLogger
from logger                                         import StdOutLogger
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
from subprocess                                     import PIPE
from subprocess                                     import Popen
from time                                           import sleep
from tkinter                                        import Button
from tkinter                                        import Checkbutton
from tkinter                                        import END
from tkinter                                        import Entry
from tkinter                                        import IntVar
from tkinter                                        import LEFT
from tkinter                                        import Label
from tkinter                                        import LabelFrame
from tkinter                                        import Listbox
from tkinter                                        import RIGHT
from tkinter                                        import StringVar
from tkinter                                        import Tk
from tkinter                                        import constants
from tkinter.messagebox                             import showerror
import errno
import io
import locale
import re

#===================================================================================================
# Implementation
#===================================================================================================
AVEL_MOR    = 'Avel Mor'
TY_AGATHE   = 'Ty Agathe'
TY_TANIA    = 'Ty Tania'
TY_PAPY     = 'Ty Papy'

CLEANING    = 'Ménage'
LOW         = 'Basse saison'
MEDIUM      = 'Moyenne saison'
HIGH        = 'Haute saison'
VERY_HIGH   = 'Très haute saison'

PRICE_WEEK = {
            AVEL_MOR:    {CLEANING:  70,
                          LOW:         550,
                          MEDIUM:      600,
                          HIGH:        700,
                          VERY_HIGH:   900},
            TY_AGATHE:   {CLEANING:  50,
                          LOW:         500,
                          MEDIUM:      550,
                          HIGH:        600,
                          VERY_HIGH:   800},
            TY_TANIA:    {CLEANING:  50,
                          LOW:         400,
                          MEDIUM:      500,
                          HIGH:        550,
                          VERY_HIGH:   700},
            TY_PAPY:     {CLEANING:  50,
                          LOW:         500,
                          MEDIUM:      550,
                          HIGH:        600,
                          VERY_HIGH:   800}
            }

PRICE_NIGHT = {
            AVEL_MOR:    {CLEANING:  100,
                          LOW:         200,
                          MEDIUM:      200},
            TY_AGATHE:   {CLEANING:  50,
                          LOW:         200,
                          MEDIUM:      200},
            TY_TANIA:    {CLEANING:  50,
                          LOW:         200,
                          MEDIUM:      200},
            TY_PAPY:     {CLEANING:  50,
                          LOW:         200,
                          MEDIUM:      200}
            }

class House(object):
    '''
    '''
    def __init__(self, name, beds):
        '''
        '''
        self.name           = name
        self.beds           = beds
    # end def __init__

    def getPrice(self, start, end):
        '''
        '''
        pass
    # end def getPrice
# end class House

Houses = {
    AVEL_MOR:   House(AVEL_MOR,  9),
    TY_AGATHE:  House(TY_AGATHE, 8),
    TY_TANIA:   House(TY_TANIA,  6),
    TY_PAPY:    House(TY_PAPY,   8),
    }

class Season(object):
    '''
    '''
    def __init__(self, start, end, seasonType):
        '''
        Constructor
        '''
        self.start      = start
        self.end        = end
        self.seasonType = seasonType
    # end def __init__

    def inDuration(self, start, end):
        '''
        '''
        if end < self.start:
            return False
        elif start > self.end:
            return False
        elif (start >= self.start) and (end <= self.end):
            return True
        else:
            raise NotImplementedError('Périodes à cheval [%s-%s] et [%s-%s]' \
                                      % (start, end, self.start, self.end))
        # end if
    # end def inDuration
# end class Season

Seasons = (
            Season('29/09/18', '01/06/19', LOW),

            Season('01/06/19', '29/06/19', MEDIUM),
            Season('29/06/19', '13/07/19', HIGH),
            Season('13/07/19', '17/08/19', VERY_HIGH),
            Season('17/08/19', '31/08/19', HIGH),
            Season('31/08/19', '28/09/19', MEDIUM),
            Season('28/09/19', '02/06/20', LOW),
            )

class ContractManager(object):
    '''
    Contract manager - manage the input and generate the contract
    '''
    def __init__(self, outputdir = None):
        '''
        Contract manager constructor
        @option outputdir [in] (str) Directory where the 
        '''
        locale.setlocale(locale.LC_ALL,'')

        if outputdir is None:
            outputdir = 'contrats'
        # end if
        self._baseOutputdir = outputdir

        self._debug         = False

        self._locataire     = None

        self._avelmor       = True
        self._tyagathe      = True
        self._tytania       = True
        self._typapy        = True

        self._start         = None
        self._end           = None

        self._ratio         = 25
        self._price         = None
        self._cleaning      = 0
        self._cleaningInc    = None
        self._beds          = None
        self._deposit       = None

        self._content       = None

        self.logger         = StdOutLogger()
    # end def __init__

    def _getDuration(self):
        '''
        '''
        return (self._end - self._start).days
    # end _getDuration
    _duration = property(_getDuration)

    def _getOutputDir(self):
        '''
        '''
        outputdir = '%s_%s' % (self._baseOutputdir, self._start.strftime('%Y'))
        outputdir = join(outputdir, self._start.strftime('%m'))
        return outputdir
#         return '%s_%s' % (self._baseOutputdir, self._start.strftime('%Y'))
    # end def _getOutputDir
    _outputdir = property(_getOutputDir)

    def _getHouseList(self):
        '''
        '''
        houseList = []

        if self._avelmor:  houseList.append(AVEL_MOR)
        if self._tyagathe: houseList.append(TY_AGATHE)
        if self._tytania:  houseList.append(TY_TANIA)
        if self._typapy:   houseList.append(TY_PAPY)

        return houseList
    # end def _getHouseList
    _houseList = property(_getHouseList)

    def _getSeason(self, start, end):
        '''
        '''
        for s in Seasons:
            if (DateTools.strToDate(start) >= DateTools.strToDate(s.start)) \
                and (DateTools.strToDate(end) <= DateTools.strToDate(s.end)):

                return s.seasonType
            # end if
        # end for
        raise ValueError('Saison non définie pour la période du %s au %s' % (start, end))
    # end def _getSeason

    def _getHousePrice(self, houseName, weekList):
        '''
        '''
        totalPrice    = 0
        cleaning = None

        for start, end in weekList:
            duration = (end - start).days
            assert ((duration <= 7) and (duration > 0))

            season      = self._getSeason(start, end)
            house       = Houses[houseName]

            priceWeek       = PRICE_WEEK[house.name][season]

            priceNight      = 30000
            if season in PRICE_NIGHT[house.name]:
                priceNight  = PRICE_NIGHT[house.name][season]
            else:
                self.logger.log('Pas de tarif à la nuit cette saison')
            # end if

            pricePerNight = self._duration*priceNight
            if (duration == 7) or (pricePerNight > priceWeek):
                # Duration = a week or price for a week is smaller
                housePrice  = priceWeek
                cleaning    = PRICE_WEEK[house.name][CLEANING]
            else:
                # Price 
                housePrice  = pricePerNight
                cleaning    = PRICE_NIGHT[house.name][CLEANING]
            # end if

            self.logger.log('Prix pour %s (%s au %s): %d Euros' % (houseName,
                                                                   DateTools.shortDate(start),
                                                                   DateTools.shortDate(end),
                                                                   housePrice))
            totalPrice += housePrice
        # end for

        self.logger.log('Ménage pour %s : %d Euros' % (houseName, cleaning))

        addText = ''
        if self._cleaningInc:
            totalPrice += cleaning
            addText = ' (ménage inclus)'
        # end if
        self.logger.log('Total pour %s : %d Euros %s' % (houseName, totalPrice, addText))
        return (totalPrice, cleaning)
    # end def _getHousePrice

    def getTotalPrice(self):
        '''
        '''
        totalPrice    = 0
        cleaning = 0

        weekList = []
        if (self._duration <= 7):
            weekList.append([self._start, self._end])
        else:
            start = self._start
            end = self._start + timedelta(7)

            while start < self._end:
                weekList.append([start, end])
                start += timedelta(7)
                end += timedelta(7)
                if end > self._end:
                    end = self._end
                # end if
            # end while
        # end if

        self._beds = 0
        for house in self._houseList:
            price, cleaning = self._getHousePrice(house, weekList)
            totalPrice += price
            cleaning += cleaning
            self._beds += Houses[house].beds
        # end for

        self._deposit = 300 * self._countHouses()

        return totalPrice, cleaning, self._beds, self._deposit
    # end def getTotalPrice

    def _countHouses(self):
        '''
        '''
        return len(self._getHouseList())
    # end def _countHouses

    def _getTemplateOdt(self):
        '''
        '''
        # Get accurate templateOdt file
        if len(self._houseList) > 1:
            templateOdt = 'TMP_Groupe.odt'
        elif self._avelmor:
            templateOdt = 'TMP_AvelMor.odt'
        elif self._tyagathe:
            templateOdt = 'TMP_TyAgathe.odt'
        elif self._tytania:
            templateOdt = 'TMP_TyTania.odt'
        elif self._typapy:
            templateOdt = 'TMP_TyPapy.odt'
        else:
            self.logger.logError('Aucun gite n\'est sélectionné !')
        # end if

        return templateOdt
    # end def _getTemplateOdt
    templateOdt = property(_getTemplateOdt)

    def _getLocataireOdt(self):
        '''
        '''
        odtFile = self.templateOdt
        assert (odtFile[-4:].lower() == '.odt')
        assert (odtFile[:4].upper() == 'TMP_')

        filename = '%s_%s_%s.odt' % (odtFile[4:-4],
                                     self._locataire.replace(' ', ''),
                                     DateTools.isoDate(self._start))
        return join(self._outputdir, filename)
    # end def _getLocataireOdt
    locataireOdt = property(_getLocataireOdt)

    def _getLocatairePdf(self):
        '''
        '''
        odtFile = self.templateOdt
        assert (odtFile[-4:].lower() == '.odt')
        assert (odtFile[:4].upper() == 'TMP_')

        filename = '%s_%s_%s.pdf' % (odtFile[4:-4],
                                     self._locataire.replace(' ', ''),
                                     DateTools.isoDate(self._start))
        return join(self._outputdir, filename)
    # end def _getLocatairePdf
    locatairePdf = property(_getLocatairePdf)

    @staticmethod
    def _cleanTmp():
        '''
        '''
        while isdir('tmp'):
            try:
                rmtree('tmp')
            except OSError:
                pass
            # end try
            if isdir('tmp'): sleep(0.5)
        # end while
    # end def _cleanTmp

    @staticmethod
    def _formatPrice(price):
        '''
        '''
        price = '%.2f' % price
        price = price.replace('.', ',')
        return price
    # end def _formatPrice

    @staticmethod
    def makedirsForce(path):
        try:
            makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and isdir(path):
                pass
            else:
                raise
        # end try
    # end def makedirsForce

    def _extractTemplate(self):
        '''
        '''
        self.logger.logDbg('extractTemplate...')

        # Delete and create tmp dir again
        self._cleanTmp()
        sleep(1)
        self.makedirsForce('tmp')

        # Unzip templat into tmp
        templatePath = join('templates', self.templateOdt)
        if not isfile(templatePath):
            self.logger.logError('Le template %s n\'existe pas !' % self.templateOdt)
            return
        # end if

        unpack_archive(filename     = templatePath,
                       extract_dir  = 'tmp',
                       format       = 'zip')
    # end def _extractTemplate

    def _replaceFields(self):
        '''
        '''
        self.logger.logDbg('replaceFields...')

        subList = (
                    ('__locataire__',   self._locataire),
                    ('__gites__',       ', '.join(self._houseList)),

                    ('__validite__',    DateTools.fullDate(date.today() + timedelta(7))),
                    ('__arrivee__',     DateTools.fullDate(self._start)),
                    ('__depart__',      DateTools.fullDate(self._end)),

                    ('__ratio__',       ('%d' % self._ratio)),
                    ('__loyer__',       self._formatPrice(self._price)),
                    ('__reste__',       self._formatPrice(self._price*(1-self._ratio/100))),
                    ('__arrhes__',      self._formatPrice(self._price*self._ratio/100)),
                    ('__lits__',        ('%d' % self._beds)),
                    ('__caution__',     ('%d' % self._deposit)),
                  )

        for tag, value in subList:
            self._content = re.sub(tag, value, self._content)
        # end for

        # Fill __menage__
        if self._cleaningInc:
            cleaning = '(ménage inclus)'
        else:
            cleaning = '%s Euros' % self._formatPrice(self._cleaning)
        # end if
        self._content = re.sub('__menage__', cleaning, self._content)

        offset = self._content.find('__')
        if (offset != -1):
            raise ValueError('Il reste la balise %s...' % self._content[offset:offset+15])
        # end if
    # end def _replaceFields

    def _loadContent(self):
        '''
        '''
        self.logger.logDbg('loadContent...')

        # Read UTF-8 text
        filename = join('tmp', 'content.xml')
        with io.open(filename,'r',encoding='utf8') as f:
            self._content = f.read()
        # process Unicode text
    # end def _loadContent

    def _saveContent(self):
        '''
        '''
        self.logger.logDbg('saveContent...')

        filename = join('tmp', 'content.xml')
        remove(filename)

        sleep(1)

        # Save UTF-8 text
        with io.open(filename,'w',encoding='utf8') as f:
            f.write(self._content)
        # end with
    # end def _saveContent

    def _saveOdt(self):
        '''
        '''
        self.logger.logDbg('saveOdt...')

        # Unzip tmp file odt file
        make_archive(base_name = self.locataireOdt,
                     format    = 'zip',
                     root_dir  = 'tmp')
        if isfile(self.locataireOdt): remove(self.locataireOdt)
        rename(self.locataireOdt + '.zip',
               self.locataireOdt)
    # end def _saveOdt

    def _convertToPdf(self):
        '''
        '''
        self.logger.logDbg('_convertToPdf...')

        # Delete PDF File if it already exists
        pdfFile = self.locatairePdf

        if isfile(pdfFile):
            try:
                remove(pdfFile)
            except PermissionError:
                self._killFoxitReader()
                remove(pdfFile)
            # end try
        # end if

        while isfile(pdfFile):
            self.logger.logDbg('Attente suppression de %s...' % pdfFile)
            sleep(0.5)
        # end while

        if not isfile(self.locataireOdt):
            raise RuntimeError('Le fichier %s n\'existe pas' % self.locataireOdt)
        # end while

#         odt2pdfpath = abspath('Odt2Pdf.bat')
#         odtFile     = basename(self.locataireOdt)
        odt2pdfpath = 'Odt2Pdf.bat'
        odtFile     = self.locataireOdt
        destDir     = dirname(self.locataireOdt)

        if not isfile(odt2pdfpath):
            raise RuntimeError('Le fichier %s n\'existe pas' % odt2pdfpath)
        # end if

        args  = u'"C:\Program Files\LibreOffice\program\soffice.exe" ' \
                ' --convert-to pdf --outdir %s %s' % (destDir, odtFile)
        self.logger.logDbg('%s' % args)
        Popen(args   = args,
              shell  = False,
              stdout = PIPE,
              stderr = PIPE,
              stdin  = PIPE)

        for _ in range(5):
            self.logger.logDbg('Attente de création de %s...' % pdfFile)
            if isfile(pdfFile):
                break
            # end if
            sleep(2)
        else:
            raise RuntimeError('Impossible de créer le fichier PDF %s' % pdfFile)
        # end while
    # end def _convertToPdf

    @staticmethod
    def _killFoxitReader():
        '''
        '''
        system('taskkill /im Foxit*')
        sleep(2)
    # end def _killFoxitReader

    def createPdf(self):
        '''
        '''
        self.logger.log('Création du fichier LibreOffice')
        self._extractTemplate()
        self._loadContent()
        self._replaceFields()
        self._saveContent()
        self._saveOdt()

        self.logger.log('Conversion du fichier en PDF')
        self._convertToPdf()
        self._cleanTmp()

        self.logger.log('Fichier %s créé' % self.locatairePdf)
    # end def createPdf

    def updateData(self, locataire,
                         start,
                         end,
                         avelMor,
                         tyAgathe,
                         tyTania,
                         tyPapy,
                         price,
                         cleaning,
                         cleaningInc):
        '''
        '''
        self._locataire     = locataire
        self._start         = start
        self._end           = end

        self._avelmor       = avelMor
        self._tyagathe      = tyAgathe
        self._tytania       = tyTania
        self._typapy        = tyPapy

        self._price         = 0 if price=='' else int(price)
        self._cleaning      = 0 if cleaning==''  else int(cleaning)
        self._cleaningInc    = cleaningInc
    # end def updateData

    def logData(self):
        '''
        '''
        self.logger.clearLog()
        if self._cleaningInc: self.logger.log('Ménage inclus')
        else: self.logger.log('Ménage en sus')
    # end def logData
# end class ContractManager

class ContractManagerGui(AbstractLogger):
    '''
    '''
    def __init__(self, contractManager):
        '''
        '''
        super(ContractManagerGui, self).__init__()

        self.fData = None
        self.contractManager = contractManager

        self._setGui()
    # end def __init__

    def _readConfig(self):
        '''
        '''
        defaultConfig = {
                  'locataire'   : 'Locataire',
                  'start'       : '11/8/2018',
                  'end'         : '25/8/2018',
                  'automatic'   : True,
                  'price'       : 1600,
                  'cleaning'    : 70,
                  'avelmor'     : True,
                  'tyagathe'    : False,
                  'tytania'     : False,
                  'typapy'      : False,
                  'cleaninginc'  : False,
                  }

        config = copy(defaultConfig)

        try:
            filename = 'contrats.ini'
            if not isfile(filename):
                return defaultConfig
            # end if
            with open(filename, 'r') as f:
                lines = f.readlines()
            # end with
    
            for line in lines:
                pos = line.find('=')
                if pos == -1:
                    continue
                # end if
    
                key   = line[:pos].strip()
                value = line[pos+1:].strip()
    
                if key not in defaultConfig.keys():
                    return defaultConfig
                else:
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    # end if
    
                    if key in ['start', 'end']:
                        DateTools.strToDate(value)
                    # end if
    
                    config[key] = value
                # end if
            # end for
        except:
            return defaultConfig
        # end try

        return config
    # end def _readConfig

    def _saveConfig(self):
        '''
        '''
        config = {}

        config['locataire']     = self._locataire
        config['start']         = DateTools.shortDate(self._start)
        config['end']           = DateTools.shortDate(self._end)
        config['automatic']     = self._automatic
        config['price']         = self._price
        config['cleaning']      = self._cleaning
        config['avelmor']       = self._avelMor
        config['tyagathe']      = self._tyAgathe
        config['tytania']       = self._tyTania
        config['typapy']        = self._tyPapy
        config['cleaninginc']   = self._cleaningInc

        filename = 'contrats.ini'
        with open(filename, 'w') as f:
            for key, value in config.items():
                f.write('%s = %s\n' % (key, value))
            # end for
        # end with
    # end def _readConfig

    def _setGui(self):
        '''
        '''
        wMain = Tk()

        config = self._readConfig()

        self.bAvelMor       = IntVar(value=1)
        self.bTyAgathe      = IntVar()
        self.bTyTania       = IntVar()
        self.bTyPapy        = IntVar()
        self.bCleaning      = IntVar()
        self.bAutoPrice     = IntVar(value=1)

        font10 = '-family {DejaVu Sans} -size 12 -weight bold -overstrike 0'
        label = Label(wMain,
                      text='Location Le Mejou',
                      font=font10)
        label.pack()


        self.fData = LabelFrame(wMain, text='Gites', padx=20)
        self.fData.pack()

        # -------------------------------------------------------------
        # String
        # -------------------------------------------------------------

        self.row          = 0
        self.dEntry       = {}
        self.dText        = {}
        self.dCheck       = {}
        self.dCheckButton = {}

        self._addText(key  = 'locataire', label = 'Nom du locataire', text = config['locataire'])
        self._addText(key  = 'start',     label = 'Date d\'arrivée',  text = config['start'])
        self._addText(key  = 'end',       label = 'Date de départ',   text = config['end'])

        self._addCheck(key = 'automatic', label = 'Prix automatique', value = config['automatic'], command = self._switchAutomatic)

        self._addText(key  = 'price',     label = 'Loyer',            text   = config['price'])
        self._lockText('price', config['automatic'])
        self._addText(key  = 'cleaning',  label  = 'Prix du ménage',  text   = config['cleaning'])
        self._lockText('cleaning', config['automatic'])
        
        self._addCheck(key = 'avelmor',   label = 'Avel Mor',         value = config['avelmor'])
        self._addCheck(key = 'tyagathe',  label = 'Ty Agathe',        value = config['tyagathe'])
        self._addCheck(key = 'tytania',   label = 'Ty Tania',         value = config['tytania'])
        self._addCheck(key = 'typapy',    label = 'Ty Papy',          value = config['typapy'])

        self._addCheck(key = 'cleaninginc', label = 'Ménage inclus',  value = config['cleaninginc'])
        self._addText(key  = 'beds',      label = 'Nombre de lits',   text = '0')
        self._lockText('beds', True)
        self._addText(key  = 'deposit',   label = 'Caution',          text = '0')
        self._lockText('deposit', True)


        # -------------------------------------------------------------
        # Log window
        # -------------------------------------------------------------

        fDetails = LabelFrame(wMain, text='Détails')
        fDetails.pack()

        self.lDetails = Listbox(fDetails, width = 60)
        self.lDetails.grid(row=self.row, columnspan=2, sticky='W')

        bProcess=Button(wMain, text = 'Générer contrat', command = self._generateContract)
        bProcess.pack(side=LEFT, padx=5, pady=5)

        bCancel=Button(wMain, text='Quitter', command=wMain.quit)
        bCancel.pack(side=RIGHT, padx=5, pady=5)

#         self.contractManager.logger = self

        self._updatePrice()

        wMain.mainloop()
    # end def _setGui

    def _addText(self, key, label, text):
        '''
        '''
        parent = self.fData

        label = Label(parent, text=label, width=25, anchor='w')
        label.grid(row=self.row, sticky='W')

        sv = StringVar()
        sv.set(text)
        sv.trace("w", lambda name, index, mode, sv=sv: self._updatePrice())                         # @UnusedVariable
        eLocataire = Entry(parent, textvariable=sv, width=25)
        eLocataire.grid(row=self.row, column=1, sticky='W')

        self.dText[key]  = sv
        self.dEntry[key] = eLocataire

        self.row += 1
    # end def _addText

    def _lockText(self, key, lock):
        '''
        '''
        if lock:
            self.dEntry[key].config(state = constants.DISABLED)
        else:
            self.dEntry[key].config(state = constants.NORMAL)
        # end if
    # end def _lockText

    def _getText(self, key):
        return self.dText[key].get()
    # end def _getKey
    def _setText(self, key, value):
        self.dText[key].set(value)
    # end def _setText

    def _getLocataire(self):
        return self._getText('locataire')
    # end def _getLocataire
    def _setLocataire(self, locataire):
        self._setText('locataire', locataire)
    # end def _setLocataire
    _locataire = property(_getLocataire, _setLocataire)

    def _getstart(self):
        return DateTools.strToDate(self._getText('start'),
                                   source = 'Début de location')
    # end def _getstart
    def _setstart(self, start):
        self._setText('start', DateTools.shortDate(start))
    # end def _setstart
    _start = property(_getstart, _setstart)

    def _getend(self):
        return DateTools.strToDate(self._getText('end'))
    # end def _getend
    def _setend(self, end):
        self._setText('end', DateTools.shortDate(end))
    # end def _setend
    _end = property(_getend, _setend)

    def _getPrice(self):
        price = self._getText('price')
        if price == '':
            return 0
        else:
            return int(price)
        # end if
    # end def _getPrice
    def _setPrice(self, price):
        self._setText('price', '%d' % price)
    # end def _setPrice
    _price = property(_getPrice, _setPrice)

    def _getBeds(self):
        beds = self._getText('beds')
        if beds == '':
            return 0
        else:
            return int(beds)
        # end if
    # end def _getBeds
    def _setBeds(self, beds):
        self._setText('beds', '%d' % beds)
    # end def _setBeds
    _beds = property(_getBeds, _setBeds)

    def _getDeposit(self):
        deposit = self._getText('deposit')
        if deposit == '':
            return 0
        else:
            return int(deposit)
        # end if
    # end def _getDeposit
    def _setDeposit(self, deposit):
        self._setText('deposit', '%d' % deposit)
    # end def _setDeposit
    _deposit = property(_getDeposit, _setDeposit)

    def _getCleaningPrice(self):
        price = self._getText('cleaning')
        if price == '':
            return 0
        else:
            return int(price)
        # end if
    # end def _getCleaningPrice
    def _setCleaningPrice(self, price):
        self._setText('cleaning', '%d' % price)
    # end def _setCleaningPrice
    _cleaning = property(_getCleaningPrice, _setCleaningPrice)

    def _addCheck(self, key, label, value, command = None):
        '''
        '''
        if command is None:
            command = self._updatePrice
        # end if

        parent = self.fData

        if value:
            value = 1
        else:
            value = 0
        # end if
        boolVar = IntVar(value = value)

        checkbutton = Checkbutton(parent,
                                  text      = label,
                                  variable  = boolVar,
                                  width     = 30,
                                  anchor    = 'w',
                                  command   = command)
        checkbutton.grid(row=self.row, columnspan=2, sticky='W')

        self.dCheck[key]       = boolVar
        self.dCheckButton[key] = checkbutton

        self.row += 1
    # end def _addCheck

    def _getBool(self, key):
        return (self.dCheck[key].get() == 1)
    # end def _getKey
    def _setBool(self, key, value):
        if value:
            value = 1
        else:
            value = 0
        # end if
        self.dCheck[key].set(value)
    # end def _setBool

    def _getAutomatic(self):
        return self._getBool('automatic')
    # end def _getAutomatic
    def _setAutomatic(self, value):
        self._setBool('automatic', value)
    # end def _setAutomatic
    _automatic = property(_getAutomatic, _setAutomatic)

    def _getCleaningInc(self):
        return self._getBool('cleaninginc')
    # end def _getCleaningInc
    def _setCleaningInc(self, value):
        self._setBool('cleaninginc', value)
    # end def _setCleaningInc
    _cleaningInc = property(_getCleaningInc, _setCleaningInc)

    def _getAvelMor(self):
        return self._getBool('avelmor')
    # end def _getAvelMor
    def _setAvelMor(self, value):
        self._setBool('avelmor', value)
    # end def _setAvelMor
    _avelMor = property(_getAvelMor, _setAvelMor)

    def _getTyAgathe(self):
        return self._getBool('tyagathe')
    # end def _getTyAgathe
    def _setTyAgathe(self, value):
        self._setBool('tyagathe', value)
    # end def _setTyAgathe
    _tyAgathe = property(_getTyAgathe, _setTyAgathe)

    def _getTyTania(self):
        return self._getBool('tytania')
    # end def _getTyTania
    def _setTyTania(self, value):
        self._setBool('tytania', value)
    # end def _setTyTania
    _tyTania = property(_getTyTania, _setTyTania)

    def _getTyPapy(self):
        return self._getBool('typapy')
    # end def _getTyPapy
    def _setTyPapy(self, value):
        self._setBool('typapy', value)
    # end def _setTyPapy
    _tyPapy = property(_getTyPapy, _setTyPapy)

    def _synchData(self):
        '''
        '''
        self.contractManager.updateData(locataire       = self._locataire,
                                        start           = self._start,
                                        end             = self._end,
                                        avelMor         = self._avelMor,
                                        tyAgathe        = self._tyAgathe,
                                        tyTania         = self._tyTania,
                                        tyPapy          = self._tyPapy,
                                        price           = self._price,
                                        cleaning   = self._cleaning,
                                        cleaningInc = self._cleaningInc,
                                        )
        self.contractManager.logData()
    # end def _synchData

    def _updatePrice(self):
        '''
        '''
        self._synchData()
        price, cleaning, beds, deposit = self.contractManager.getTotalPrice()

        self._beds = beds
        self._deposit = deposit

        if self._automatic:
            self._price = price
            self._cleaning = cleaning
        # end if
    # end def _updatePrice

    def _switchAutomatic(self):
        '''
        '''
        self._lockText('price', self._automatic)
        self._lockText('cleaning', self._automatic)
        self._updatePrice()
    # end def _switchAutomatic

    @staticmethod
    def _openExplorer(path = None):
        '''
        '''
        args = ['explorer.exe', ]
        if isdir(path):
            args.append(path)
        elif isfile(path):
            args.append('/select,%s' % path)
        # end if
        Popen(args = args)
    # end def _openExplorer

    def _generateContract(self):
        '''
        '''
        self.log('Mise à jour des prix')
        self._updatePrice()

        self.contractManager.createPdf()
        self._saveConfig()
        self._openExplorer(self.contractManager.locatairePdf)
    # end def _generateContract

    def clearLog(self):
        '''
        '''
        self.lDetails.delete(0, END)
    # end def clearLog

    def log(self, msg):
        '''
        '''
        self.lDetails.insert(END, msg)
    # end def log

    def logError(self, msg):
        '''
        '''
        showerror(msg)
    # end def logError
# end class ContractManagerGui


#===================================================================================================
# Main
#===================================================================================================

if (__name__ == '__main__'):
    cm = ContractManager()
    gui = ContractManagerGui(cm)
# end if


#===================================================================================================
# End
#===================================================================================================
