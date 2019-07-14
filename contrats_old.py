# -*- coding: utf-8 -*-

from datetime                                       import date
from datetime                                       import timedelta
from os                                             import makedirs
from os                                             import remove
from os                                             import rename
from os                                             import system
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
from tkinter.messagebox                             import showerror
import errno
import io
import locale
import re

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

class DateTools(object):
    '''
    '''
    @staticmethod
    def strToDate(strDate):
        '''
        '''
        listDate = strDate.split('/')
        if len(listDate) != 3:
            print('La date n\'est pas au format \'jour/mois/année\'')
            print('Saisissez à nouveau !')

            raise ValueError('La date n\'est pas au format \'jour/mois/année\'')
        # end if
        day, month, year = [int(i) for i in listDate]
        if year <= 99:
            year += 2000
        # end if
        return date(year, month, day)
    # end def strToDate

    @staticmethod
    def isoDate(rawDate):
        '''
        '''
        return rawDate.strftime('%Y%m%d')
    # end def isoDate

    @staticmethod
    def shortDate(rawDate):
        '''
        '''
        return rawDate.strftime('%d/%m/%Y')
    # end def shortDate

    @staticmethod
    def fullDate(rawDate):
        '''
        '''
        return rawDate.strftime('%A %d %B %Y')
    # end def fullDate
# end class DateTools

class AbstractLogger(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self._debug = False
    # end def __init__

    def clearLog(self):
        '''
        '''
        raise NotImplementedError
    # end def clearLog

    def log(self, msg):
        '''
        '''
        raise NotImplementedError
    # end def log

    def logError(self, msg):
        '''
        '''
        raise NotImplementedError
    # end def logError

    def logDbg(self, msg):
        '''
        '''
        if self._debug: self.log(msg)
    # end def logDbg
# end class AbstractLogger

class StdOutLogger(AbstractLogger):
    '''
    '''
    def clearLog(self):
        '''
        '''
        pass
    # end def clearLog

    def log(self, msg):
        '''
        '''
        print(msg)
    # end def log

    def logError(self, msg):
        '''
        '''
        print(msg)
    # end def logError
# end class StdOutLogger

class Price(object):
    '''
    '''
    def __init__(self, start, end, night, weekend, week):
        '''
        '''
        self.start    = DateTools.strToDate(start)
        self.end      = DateTools.strToDate(end)
        self.night    = night
        self.weekend  = weekend
        self.week     = week
    # end def __init__

    def __str__(self):
        return '%s - %s : %d/%d/%d' % (DateTools.shortDate(self.start),
                                       DateTools.shortDate(self.end),
                                       self.night,
                                       self.weekend,
                                       self.week,
                                       )
    # end def __str__
# end class Price

class YesNo(object):
    '''
    '''
    def __init__(self, boolean):
        '''
        '''
        self._boolean = boolean
    # end def __init__

    def __str__(self):
        '''
        '''
        if self._boolean:
            return 'Oui'
        else:
            return 'Non'
        # end if
    # end def

    def __bool__(self):
        return self._boolean
    # end def __bool__
# end class YesNo

class HOUSES(object):
    '''
    '''
    AVEL_MOR  = 'Avel Mor'
    TY_AGATHE = 'Ty Agathe'
    TY_TANIA  = 'Ty Tania'
    TY_PAPY   = 'Ty Papy'
# end class HOUSES

class House(object):
    '''
    '''
    def __init__(self, name, cleaningPrice, beds, prices):
        '''
        '''
        self.name           = name
        self.cleaningPrice  = cleaningPrice
        self.beds           = beds
        self.prices         = prices
    # end def __init__
# end class House

Houses = {
    HOUSES.AVEL_MOR: 
        House(name          = HOUSES.AVEL_MOR,
              cleaningPrice = 70,
              beds          = 9,
              prices        = (
                                Price('1/1/18',  '1/6/18',  200,  400,  500),
                                Price('2/6/18',  '7/7/18',  200,  400,  550),
                                Price('7/7/18',  '13/7/18', None, None, 700),
                                Price('14/7/18', '17/8/18', None, None, 950),
                                Price('18/8/18', '24/8/18', None, None, 700),
                                Price('25/8/18', '28/9/18', 200,  400,  550),
                                Price('29/9/18', '1/6/19',  200,  400,  500),
                                ),
              ),
    HOUSES.TY_AGATHE:
        House(name          = HOUSES.TY_AGATHE,
              cleaningPrice = 50,
              beds          = 8,
              prices        = (
                                Price('1/1/18',  '1/6/18',  200,  400,  450),
                                Price('2/6/18',  '7/7/18',  200,  400,  500),
                                Price('7/7/18',  '13/7/18', None, None, 600),
                                Price('14/7/18', '17/8/18', None, None, 800),
                                Price('18/8/18', '24/8/18', None, None, 600),
                                Price('25/8/18', '28/9/18', 200,  400,  500),
                                Price('29/9/18', '1/6/19',  200,  400,  450),
                                )
              ),
    HOUSES.TY_TANIA:
        House(name          = HOUSES.TY_AGATHE,
              cleaningPrice = 50,
              beds          = 6,
              prices        = (
                                Price('1/1/18',  '1/6/18',  200,  400,  350),
                                Price('2/6/18',  '7/7/18',  200,  400,  400),
                                Price('7/7/18',  '13/7/18', None, None, 450),
                                Price('14/7/18', '17/8/18', None, None, 700),
                                Price('18/8/18', '24/8/18', None, None, 450),
                                Price('25/8/18', '28/9/18', 200,  400,  400),
                                Price('29/9/18', '1/6/19',  200,  400,  350),
                                ),
              ),
    HOUSES.TY_PAPY:
        House(name          = HOUSES.TY_AGATHE,
              cleaningPrice = 50,
              beds          = 8,
              prices        = (
                                Price('1/1/18',  '1/6/18',  200,  400,  450),
                                Price('2/6/18',  '7/7/18',  200,  400,  500),
                                Price('7/7/18',  '13/7/18', None, None, 600),
                                Price('14/7/18', '17/8/18', None, None, 800),
                                Price('18/8/18', '24/8/18', None, None, 600),
                                Price('25/8/18', '28/9/18', 200,  400,  500),
                                Price('29/9/18', '1/6/19',  200,  400,  450),
                                ),
              ),
    }

class Setter(object):
    '''
    '''
    def __init__(self, logger = None):
        '''
        '''
        self._logger            = logger
        self._locataire         = None
        self._avelmor           = None
        self._tyagathe          = None
        self._tytania           = None
        self._typapy            = None
        self._start             = None
        self._end               = None
        self._price             = None
        self._cleaningPrice     = None
        self._cleaningIncluded  = None
    # end def __init__

    def _inputInt(self, msg,
                        default = None):
        '''
        '''
        formattedInt = None

        while formattedInt is None:
            try:
                rawInt = self._inputString(msg, default)
                formattedInt = int(rawInt)
            except:  #pylint: disable=bare-except
                self._logger.logError('Impossible de lire le montant. Saisissez à nouveau !')
                continue
            # end try
        # end while

        return formattedInt
    # end def _inputInt

    def inputData(self, locataire = None,
                        avelmor   = None,
                        tyagathe  = None,
                        tytania   = None,
                        typapy    = None,
                        start    = None,
                        end   = None,
                        cleaning  = None,
                        ):
        '''
        '''
        self._locataire = self._inputString(msg      = 'Nom du locataire',
                                          default  = locataire)

        print('')
        self._avelmor   = self._inputBoolean(msg     = HOUSES.AVEL_MOR,
                                           default = avelmor)
        self._tyagathe  = self._inputBoolean(msg     = HOUSES.TY_AGATHE,
                                           default = tyagathe)
        self._tytania   = self._inputBoolean(msg     = HOUSES.TY_TANIA,
                                           default = tytania)
        self._typapy    = self._inputBoolean(msg     = HOUSES.TY_PAPY,
                                           default = typapy)

        print('')
        self._start    = self._inputDate(msg        = 'Date d\'arrivée',
                                        dateMin    = date.today(),
                                        default    = start)

        if end is None:
            self._end   = self._start + timedelta(7)
        else:
            self._end   = DateTools.strToDate(end)
        # end if
        self._end   = self._inputDate(msg        = 'Date de départ',
                                        dateMin    = self._start,
                                        default    = DateTools.shortDate(self._end))

        self._cleaningIncluded  = self._inputBoolean(msg     = 'Ménage inclus',
                                                   default = cleaning)

#         if price is None:
#             price, cleaningPrice = self.getTotalPrice()
#             self._cleaningPrice = cleaningPrice
#         # end if
#         self._price    = self._inputInt(msg          = 'Loyer',
#                                        default      = '%d' % price)

        print('')
    # end def inputData

    @staticmethod
    def _inputString(msg, default = None):
        '''
        '''
        if default is not None:
            msg += ' (par défaut = %s)' % default
        # end if
        msg += ' = '

        response = input(msg)
        if response == '':
            response = default
        # end if

        return response
    # end def _inputString

    def _inputBoolean(self, msg,
                            default = None):
        '''
        '''
        formattedBool = None

        while formattedBool is None:
            try:
                rawBool = self._inputString(msg, default)
                rawBool = rawBool.upper()
                if rawBool in ('O', 'OUI'):
                    formattedBool = YesNo(True)
                elif rawBool in ('N', 'NON'):
                    formattedBool = YesNo(False)
                else:
                    self._logger.logError('Seules les réponse \'O\' ou \'N\' sont acceptées. Saississez à nouveau!')

            except:  #pylint: disable=bare-except
                self._logger.logError('Impossible de lire le choix (O/N), saisissez à nouveau !')
                continue
            # end try
        # end while

        return formattedBool
    # end def _inputBoolean

    def _inputDate(self, msg,
                        dateMin,
                        default = None):
        '''
        '''
        formattedDate = None

        while formattedDate is None:
            try:
                strDate = self._inputString(msg, default)
                if DateTools.strToDate(strDate) <= dateMin:
                    self._logger.logError('La date doit étre dans le futur. Saisissez à nouveau !')
                    continue
                # end if
                formattedDate = DateTools.strToDate(strDate)
            except:  #pylint: disable=bare-except
                self._logger.logError('Impossible de lire la date. Saisissez à nouveau !')
                continue
            # end try
        # end while

        return formattedDate
    # end def _inputDate

# end class Setter

class ContractManager(object):
    '''
    '''
    def __init__(self, outputdir = None):
        '''
        '''
        locale.setlocale(locale.LC_ALL,'')

        if outputdir is None:
            outputdir = 'contrats'
        # end if
        self._baseOutputdir     = outputdir

        self._debug             = False

        self._locataire         = None

        self._avelmor           = True
        self._tyagathe          = True
        self._tytania           = True
        self._typapy            = True

        self._start             = None
        self._end               = None

        self._ratio             = 25
        self._price             = None
        self._cleaningPrice     = 0
        self._cleaningIncluded  = None
        self._beds              = None
        self._deposit           = None

        self._content           = None

        self.logger             = StdOutLogger()
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

        if self._avelmor:  houseList.append(HOUSES.AVEL_MOR)
        if self._tyagathe: houseList.append(HOUSES.TY_AGATHE)
        if self._tytania:  houseList.append(HOUSES.TY_TANIA)
        if self._typapy:   houseList.append(HOUSES.TY_PAPY)

        return houseList
    # end def _getHouseList
    _houseList = property(_getHouseList)

    def _getHousePrice(self, houseName, weekList):
        '''
        '''
        totalPrice    = 0
        cleaningPrice = None

        for start, end in weekList:
            duration = (end - start).days
            assert ((duration <= 7) and (duration > 0))

            housePrice = None
            cleaningPrice = None

            house = Houses[houseName]
            for price in house.prices:
                cleaningPrice = house.cleaningPrice

                if (start >= price.start) and (start <= price.end):
                    if (duration == 7):
                        housePrice = price.week
                    else:
                        if price.night is None:
                            raise ValueError('Pas de prix à la nuit au %s' % DateTools.shortDate(start))
                        housePrice = min(self._duration*price.night, price.week)
                    # end if

                    self.logger.log('Prix pour %s (%s au %s): %d Euros' % (houseName,
                                                                           DateTools.shortDate(start),
                                                                           DateTools.shortDate(end),
                                                                           housePrice))
                    totalPrice += housePrice
                    break
                # end if
            # end if

            if housePrice is None:
                raise ValueError('Il manque les prix de %s à la date du %s' % (house,
                                                                               DateTools.shortDate(start)))
            # end if
        # end for

        self.logger.log('Ménage pour %s : %d Euros' % (houseName, cleaningPrice))
        if self._cleaningIncluded:
            totalPrice += cleaningPrice
        # end if
        self.logger.log('Total pour %s : %d Euros' % (houseName, totalPrice))
        return (totalPrice, cleaningPrice)
    # end def _getHousePrice

    def getTotalPrice(self):
        '''
        '''
        totalPrice    = 0
        cleaningPrice = 0

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
            cleaningPrice += cleaning
            self._beds += Houses[house].beds
        # end for

        self._deposit = 300 * self._countHouses()

        return totalPrice, cleaningPrice, self._beds, self._deposit
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
            except OSError as excp:         # @UnusedVariable
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

    def _extractTemplate(self):
        '''
        '''
        self.logger.logDbg('extractTemplate...')

        # Delete and create tmp dir again
        self._cleanTmp()
        sleep(1)
        makedirsForce('tmp')

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
        if self._cleaningIncluded:
            cleaning = '(ménage inclus)'
        else:
            cleaning = '%s Euros' % self._formatPrice(self._cleaningPrice)
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

        args = ['Odt2Pdf.bat',
                self.locataireOdt,
                self._outputdir,
                ]
        Popen(args   = args,
              shell  = True,
              stdout = PIPE,
              stderr = PIPE,
              stdin  = PIPE)

        sleep(3)
        while not isfile(pdfFile):
            self.logger.logDbg('Attente de création de %s...' % pdfFile)
            sleep(2)
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
        self._extractTemplate()
        self._loadContent()
        self._replaceFields()
        self._saveContent()
        self._saveOdt()
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
                         cleaningPrice,
                         cleaningIncluded):
        '''
        '''
        self._locataire         = locataire
        self._start             = start
        self._end               = end

        self._avelmor           = avelMor
        self._tyagathe          = tyAgathe
        self._tytania           = tyTania
        self._typapy            = tyPapy

        self._price             = 0 if price=='' else int(price)
        self._cleaningPrice     = 0 if cleaningPrice==''  else int(cleaningPrice)
        self._cleaningIncluded  = cleaningIncluded
    # end def updateData

    def logData(self):
        '''
        '''
        self.logger.clearLog()
        if self._cleaningIncluded: self.logger.log('Ménage inclus')
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

        self.contractManager = contractManager
        self._setGui()
    # end def __init__

    def _setGui(self):
        '''
        '''
        wMain = Tk()

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


        fData = LabelFrame(wMain, text='Gites', padx=20)
        fData.pack()

        # -------------------------------------------------------------
        # String
        # -------------------------------------------------------------

        self.row = 0
        self.dText = {}
        self.dBool = {}

        self._addText(key  = 'locataire', parent = fData, label = 'Nom du locataire', text = 'Locataire')
        self._addText(key  = 'start',     parent = fData, label = 'Date d\'arrivée',  text = '11/8/2018')
        self._addText(key  = 'end',       parent = fData, label = 'Date de départ',   text = '25/8/2018')

        self._addCheck(key ='automatic',  parent = fData, label = 'Prix automatique', value = True)

        self._addText(key  = 'price',     parent = fData, label = 'Loyer',            text   = '')
        self._addText(key  = 'cleaningprice', parent = fData, label  = 'Prix du ménage',  text   = '')

        self._addCheck(key ='avelmor',    parent = fData, label = 'Avel Mor',         value = True)
        self._addCheck(key ='tyagathe',   parent = fData, label = 'Ty Agathe',        value = False)
        self._addCheck(key ='tytania',    parent = fData, label = 'Ty Tania',         value = False)
        self._addCheck(key ='typapy',     parent = fData, label = 'Ty Papy',          value = False)

        self._addCheck(key ='cleaningincluded', parent = fData, label = 'Ménage inclus',    value = False)
        self._addText(key  = 'beds',      parent = fData, label = 'Nombre de lits',   text = '0')
        self._addText(key  = 'deposit',   parent = fData, label = 'Caution',          text = '0')


        # -------------------------------------------------------------
        # Log window
        # -------------------------------------------------------------

        fDetails = LabelFrame(wMain, text='Détails')
        fDetails.pack()

        self.lDetails = Listbox(fDetails, width = 60)
        self.lDetails.grid(row=self.row, columnspan=2, sticky='W')

        bProcess=Button(wMain, text='Générer contrat', command=self._generatePdf)
        bProcess.pack(side=LEFT, padx=5, pady=5)

        bCancel=Button(wMain, text='Quitter', command=wMain.quit)
        bCancel.pack(side=RIGHT, padx=5, pady=5)

        self.contractManager.logger = self

        self._updatePrice()

        wMain.mainloop()
    # end def _setGui

    def _addText(self, key, parent, label, text):
        '''
        '''
        label = Label(parent, text=label, width=25, anchor='w')
        label.grid(row=self.row, sticky='W')

        stringVar = StringVar()
        stringVar.set(text)
        eLocataire = Entry(parent, textvariable=stringVar, width=25)
        eLocataire.grid(row=self.row, column=1, sticky='W')

        self.dText[key] = stringVar

        self.row += 1
    # end def _addText

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
        return DateTools.strToDate(self._getText('start'))
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
        price = self._getText('cleaningprice')
        if price == '':
            return 0
        else:
            return int(price)
        # end if
    # end def _getPrice
    def _setCleaningPrice(self, price):
        self._setText('cleaningprice', '%d' % price)
    # end def _setCleaningPrice
    _cleaningPrice = property(_getCleaningPrice, _setCleaningPrice)

    def _addCheck(self, key, parent, label, value):
        if value:
            value = 1
        else:
            value = 0
        # end if
        boolVar = IntVar(value = value)

        checkbutton = Checkbutton(parent, text=label, variable=boolVar, width=30, anchor='w', command=self._updatePrice)
        checkbutton.grid(row=self.row, columnspan=2, sticky='W')

        self.dBool[key] = boolVar

        self.row += 1
    # end def _addCheck

    def _getBool(self, key):
        return (self.dBool[key].get() == 1)
    # end def _getKey
    def _setBool(self, key, value):
        if value:
            value = 1
        else:
            value = 0
        # end if
        self.dBool[key].set(value)
    # end def _setBool

    def _getAutomatic(self):
        return self._getBool('automatic')
    # end def _getAutomatic
    def _setAutomatic(self, value):
        self._setBool('automatic', value)
    # end def _setAutomatic
    _automatic = property(_getAutomatic, _setAutomatic)

    def _getCleaningIncluded(self):
        return self._getBool('cleaningincluded')
    # end def _getCleaningIncluded
    def _setCleaningIncluded(self, value):
        self._setBool('cleaningincluded', value)
    # end def _setCleaningIncluded
    _cleaningIncluded = property(_getCleaningIncluded, _setCleaningIncluded)

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
                                        cleaningPrice   = self._cleaningPrice,
                                        cleaningIncluded = self._cleaningIncluded,
                                        )
        self.contractManager.logData()
    # end def _synchData

    def _updatePrice(self):
        '''
        '''
        self._synchData()
        price, cleaningPrice, beds, deposit = self.contractManager.getTotalPrice()

        self._beds = beds
        self._deposit = deposit

        if self._automatic:
            self._price = price
            self._cleaningPrice = cleaningPrice
        # end if
    # end def _updatePrice

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

    def _generatePdf(self):
        '''
        '''
        self._updatePrice()
        self.contractManager.createPdf()
        self._openExplorer(self.contractManager.locatairePdf)
    # end def _generatePdf

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

if (__name__ == '__main__'):
    cm = ContractManager()
    gui = ContractManagerGui(cm)
# end if
