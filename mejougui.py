'''
@copyright Stéphane Thomas - 2018-2021
Générateur de contrat pour Le Mejou - https://mejou.fr
'''

#===================================================================================================
# Standard Imports
#===================================================================================================

from configparser                                   import ConfigParser
from datetime                                       import date
from datetime                                       import timedelta
from functools                                      import partial
from os.path                                        import isdir
from os.path                                        import isfile
from subprocess                                     import Popen

from tkinter                                        import Button
from tkinter                                        import Checkbutton
from tkinter                                        import END
from tkinter                                        import Entry
from tkinter                                        import IntVar
from tkinter                                        import LEFT
from tkinter                                        import Label
from tkinter                                        import LabelFrame
from tkinter                                        import OptionMenu
from tkinter                                        import RIGHT
from tkinter                                        import Radiobutton
from tkinter                                        import StringVar
from tkinter                                        import Tk
from tkinter                                        import constants
from tkinter.messagebox                             import showerror
from tkinter.ttk                                    import Frame
from tkinter.ttk                                    import Notebook

from tkcalendar                                     import Calendar

#===================================================================================================
# Third party Imports
#===================================================================================================


#===================================================================================================
# Personal Imports
#===================================================================================================

from mejoucalendar                                  import GITE_LIST
from mejoucalendar                                  import MejouCalendar
from mejouconst                                     import TY_AGATHE
from mejouconst                                     import TY_PAPY
from mejoucontractmanager                           import AVEL_MOR
from mejoucontractmanager                           import ContractManager
from mejoudate                                      import MejouDate
from mejoulogger                                    import StdOutLogger
from mejourent                                      import MejouRentDate
from mejoutools                                     import price_to_str
from mejoutools                                     import str_to_price

#===================================================================================================
# Types
#===================================================================================================

COLUMNS = {AVEL_MOR:  2,
           TY_AGATHE: 3,
           TY_PAPY:   4,
           'BLOCK':   5,
           'CANCEL':  6,
           }
class COL:                                                                                          #pylint: disable=too-few-public-methods
    ''' Column width values '''
    DATES    = 17
    CLIENT   = 20
    HOUSE    = 6
    BLOCK    = 6
    CANCEL   = 6
# end class COL

class TitleLabel(Frame):                                                                            #pylint: disable=too-many-ancestors
    ''' Label for displaying rent informations'''
    def __init__(self, master):
        Frame.__init__(self, master)

        # pylint: disable=line-too-long
        titles = ('Dates',   'Client',   'Avel Mor', 'Ty Agathe', 'Ty Papy', 'Bloquer', 'Annuler')
        widths = (COL.DATES, COL.CLIENT, COL.HOUSE,  COL.HOUSE,   COL.HOUSE, COL.BLOCK, COL.CANCEL)
        # pylint: enable=line-too-long

        column = 0
        for text, width in zip(titles, widths):
            l_title = Label(self,
                            text   = text,
                            width  = width,
                            anchor = 'w',
                            )
            l_title.grid(row=0, column=column)
            column += 1
        # end for
    # end def __init__
# end class TitleLabel

class RentLabel(Frame):                                                                             #pylint: disable=too-many-ancestors
    ''' Label for displaying rent informations'''
    def __init__(self, master, rents, validate, cancel):
        Frame.__init__(self, master)

        column = 0

        start = rents[0].start.strftime("%d/%m/%y")
        end   = rents[0].end.strftime("%d/%m/%y")

        # Column #1: Add label for start/end dates
        # ----------------------------------------
        Label(self,
              text   = f'{start}-{end}',
              width  = COL.DATES,
              anchor = 'w').grid(row=0, column=column)
        column += 1

        # Column #2: Add label for client name
        # ------------------------------------
        client_name = rents[0].client
        Label(self,
              text   = client_name,
              width  = COL.CLIENT,
              anchor = 'w',
              ).grid(row=0, column=column)

        # Column #3-5: Add buttons houses
        # -------------------------------
        house_list = [rent.house for rent in rents]

        occupied = True

        for rent in rents:
            if rent.occupied:
                b_client = Button(self, text='Occupé', bg='green', fg='white', width=COL.HOUSE)
            else:
                occupied = False
                b_client = Button(self, text='Libre', bg='red', fg='white', width=COL.HOUSE)
            # end if

            b_client.grid(row=0, column=COLUMNS[rent.house])
        # end for

        # Fill house not reserved with a grey button and text ='-'
        for house in GITE_LIST:
            if house not in house_list:
                Button(self,
                       text  = '-',
                       bg    = 'grey',
                       fg    = 'black',
                       width = COL.HOUSE).grid(row=0, column=COLUMNS[house])
            # end if
        # end for

        # Column #6: Add buttons Validate
        # -------------------------------
        if occupied:
            Button(self,
                   text    = '-',
                   bg      = 'grey',
                   fg      = 'black',
                   width   = COL.BLOCK).grid(row=0, column=COLUMNS['BLOCK'])
        else:
            action = partial(validate, client = client_name, start = start, end = end)
            Button(self,
                   text    = 'Bloquer',
                   bg      = 'orange',
                   fg      = 'white',
                   width   = COL.BLOCK,
                   command = action).grid(row=0, column=COLUMNS['BLOCK'])
        # end if

        # Column #7: Add buttons Cancel
        # -----------------------------
        action = partial(cancel, client = client_name, start = start, end = end)
        Button(self,
               text    = 'Annuler',
               bg      = 'red',
               fg      = 'white',
               width   = COL.CANCEL,
               command = action).grid(row=0, column=COLUMNS['CANCEL'])
    # end def __init__
# end class RentLabel


#===================================================================================================
# Constants
#===================================================================================================

INI_CONTRATS = 'mejoucontrats.ini'


#===================================================================================================
# Implementation
#===================================================================================================

class MejouConfig():                                                                                #pylint: disable=too-few-public-methods
    ''' Manage config file '''
    LOCATAIRE = 'locataire'
    DEBUT = 'debut'
    FIN = 'fin'
    AUTOMATIQUE = 'automatique'
    PRIX = 'prix'
    TAXE = 'taxe'
    TAXEANNEE = 'taxeannee'
    DRAPS = 'draps'
    LINGE = 'linge'
    CHAUFFAGE = 'chauffage'
    MENAGE = 'menage'
    MENAGEINCLUS = 'menageinclus'
    CAUTION = 'caution'
    AVELMOR = 'avelmor'
    TYAGATHE = 'tyagathe'
    TYPAPY = 'typapy'
    CALENDRIER = 'calendrier'
# end class MejouConfig

class ContractManagerGui():                                                                         #pylint: disable=too-many-instance-attributes, too-many-public-methods
    ''' Class for contract GUI '''
    def __init__(self, cmgr):
        '''
        Class constructor
        @param cmgr [in] (ContractManager) Contract manager object
        '''
        super().__init__()

        self.debug          = True

        self.logger         = StdOutLogger()

        self.w_form         = None
        self.n_notebook     = None
        self.f_contract     = None
        self.f_calendar     = None

        self.f_data         = None
        self.cmgr           = cmgr

        self._calendar      = None

        self._gui_starting  = True

        self.b_auto_price   = None
        self.b_avelmor      = None
        self.b_cleaning     = None
        self.b_tyagathe     = None
        self.b_typapy       = None

        self.row            = None
        self.d_calendar     = None
        self.d_check        = None
        self.d_check_button = None
        self.d_entry        = None
        self.d_radio        = None
        self.d_text         = None
        self.l_calendar     = None
        self.l_details      = None

        self.with_calendar  = False

        self._setup_gui()
    # end def __init__

    @staticmethod
    def _read_config():
        ''' Read the config file '''
        config = ConfigParser()

        today = date.today()
        tomorrow = today + timedelta(days=1)

        default_config = {MejouConfig.LOCATAIRE    : 'Locataire',
                          MejouConfig.DEBUT        : today.strftime('%d/%m/%Y'),
                          MejouConfig.FIN          : tomorrow.strftime('%d/%m/%Y'),
                          MejouConfig.AUTOMATIQUE  : 'True',
                          MejouConfig.PRIX         : '1600',
                          MejouConfig.TAXE         : '1,00',
                          MejouConfig.TAXEANNEE    : '2021',
                          MejouConfig.DRAPS        : '12,00',
                          MejouConfig.LINGE        : '7,00',
                          MejouConfig.CHAUFFAGE    : '70,00',
                          MejouConfig.MENAGE       : '70',
                          MejouConfig.MENAGEINCLUS : 'False',
                          MejouConfig.CAUTION      : '70',
                          MejouConfig.AVELMOR      : 'True',
                          MejouConfig.TYAGATHE     : 'False',
                          MejouConfig.TYPAPY       : 'False',
                          MejouConfig.CALENDRIER   : 'False',
                          }

        config.read(INI_CONTRATS)

        config2 = {}

        for key in default_config:
            if key in config['Location'].keys():
                config2[key] = config['Location'][key]
            else:
                config2[key] = default_config[key]
            # end if

            if key in ('prix', 'taxe', 'draps', 'linge', 'chauffage', 'menage', 'caution'):
                config2[key] = str_to_price(config2[key])
            # end if

            if key in ('automatique', 'avelmor', 'tyagathe',
                       'typapy', 'menageinclus', 'calendrier'):
                if config2[key].lower() in ('true', 'yes', 'oui'):
                    config2[key] = True
                elif config2[key].lower() in ('false', 'no', 'non'):
                    config2[key] = False
                else:
                    raise ValueError(f'Mauvais valeur pour clé {key}: {config2[key]}')
                # end if
            # end if
        # end for

        return config2
    # end def _read_config

    def _save_config(self):
        ''' Save the config file '''
        config = ConfigParser()
        config['Location'] = {
                              # 'mr_mme'      : self._mr_mme,
                              MejouConfig.LOCATAIRE   : self._locataire,
                              MejouConfig.DEBUT       : MejouDate.short_date(self._start),
                              MejouConfig.FIN         : MejouDate.short_date(self._end),
                              MejouConfig.AUTOMATIQUE : self._automatic,
                              MejouConfig.PRIX        : self._price,
                              MejouConfig.TAXE        : self._tax,
                              MejouConfig.DRAPS       : self._sheets,
                              MejouConfig.LINGE       : self._towels,
                              MejouConfig.CHAUFFAGE   : self._heating,
                              MejouConfig.MENAGE      : self._cleaning,
                              MejouConfig.AVELMOR     : self._avelmor,
                              MejouConfig.TYAGATHE    : self._tyagathe,
                              MejouConfig.TYPAPY      : self._typapy,
                              MejouConfig.MENAGEINCLUS: self._cleaning_inc,
                              MejouConfig.CALENDRIER  : self.with_calendar,
                              }

        with open(INI_CONTRATS, mode='w', encoding='utf-8') as configfile:
            config.write(configfile)
        # end with
    # end def _save_config

    def _setup_gui(self):
        ''' Setup GUI '''
        # Setup Window...
        self.w_form = Tk()
        # ...and a notebook to manage tabs
        self.n_notebook = Notebook(self.w_form)

        # Setup Contract frame in tab 'Contrat'
        self.f_contract = Frame(self.n_notebook)
        self.n_notebook.add(self.f_contract, text = 'Contrat')

        # Setup Calendar frame in tab 'Calendrier'
        self.f_calendar = Frame(self.n_notebook)
        self.n_notebook.add(self.f_calendar, text = 'Calendrier')
        self.n_notebook.pack(expand = 1, fill = 'both')

        # Setup Contract frame
        self._setup_contract()

        if self.with_calendar:
            # Setup Calendar frame
            self._setup_calendar()
        # end if

        # Run Gui itself
        self.f_contract.mainloop()
    # end def _setup_gui

    def _setup_contract(self):                                                                      #pylint: disable=too-many-statements
        ''' Setup contract manager '''
        config = self._read_config()
        self.with_calendar  = config['calendrier']

        self.b_avelmor      = IntVar(value = 1)
        self.b_tyagathe     = IntVar()
        self.b_typapy       = IntVar()
        self.b_cleaning     = IntVar()
        self.b_auto_price   = IntVar(value = 1)

        font_title = '-family {DejaVu Sans} -size 14 -weight bold -overstrike 0'
        l_label = Label(self.f_contract,
                        text = 'Contrats de Location Le Mejou',
                        font = font_title)
        l_label.pack()

        self.f_data = LabelFrame(self.f_contract, text='Gites', padx=20)
        self.f_data.pack()

        # -------------------------------------------------------------
        # String
        # -------------------------------------------------------------

        self.row            = 0

        self.d_entry        = {}
        self.d_text         = {}
        self.d_check        = {}
        self.d_check_button = {}
        self.d_calendar     = {}
        self.d_radio        = {}

        #pylint: disable=line-too-long
        # self._add_radio(key = 'titre',     label = 'Titre',            values = ('M.', 'Mme'))
        self._add_text(key  = 'locataire', label = 'Nom du locataire', text  = config['locataire'], update = False)

        self._add_calendar(key = 'start',  label = 'Date d\'arrivée',  date  = config['debut'])
        self._add_calendar(key = 'end',    label = 'Date de départ',   date  = config['fin'])

        self._add_check(key = 'automatic', label = 'Prix automatique', value = config['automatique'], command = self._switch_automatic)

        self._add_price(key  = 'price',    label = 'Loyer',            value = config['prix'])
        self._lock_text('price', config['automatique'])
        self._add_price(key  = 'cleaning', label  = 'Prix du ménage',  value = config['menage'])
        self._lock_text('cleaning', config['automatique'])
        self._add_price(key  = 'tax',      label = 'Taxe de séjour (€/j/per)',   value = config['taxe'])
        self._add_text(key  = 'taxyear',   label = 'Taxe - année',     text  = config['taxeannee'])
        self._add_price(key  = 'sheets',   label = 'Draps',            value = config['draps'])
        self._add_price(key  = 'towels',   label = 'Linge',            value = config['linge'])
        self._add_price(key  = 'heating',  label = 'Chauffage',        value = config['chauffage'])

        self._add_check(key = 'avelmor',   label = 'Avel Mor',         value = config['avelmor'])
        self._add_check(key = 'tyagathe',  label = 'Ty Agathe-Tania',  value = config['tyagathe'])
        self._add_check(key = 'typapy',    label = 'Ty Papy',          value = config['typapy'])

        self._add_check(key = 'cleaninginc', label = 'Ménage inclus',  value = config['menageinclus'])

        self._add_text(key  = 'beds',      label = 'Nombre de couchages', text = '0')
        self._lock_text('beds', True)
        self._add_price(key  = 'deposit',  label = 'Caution',          value = config['caution'])
        self._lock_text('deposit', True)
        #pylint: enable=line-too-long


        # -------------------------------------------------------------
        # Log window
        # -------------------------------------------------------------

        # from tkinter                                        import Listbox
        # if self.debug:
        #     f_details = LabelFrame(self.f_contract, text='Détails')
        #     f_details.pack()
        #
        #     self.l_details = Listbox(f_details, width = 60)
        #     self.l_details.grid(row=self.row, columnspan=2, sticky='W')
        #     self.row += 1
        # # end if

        b_process = Button(self.f_contract,
                           text = 'Générer contrat',
                           command = self._generate_contract)
        b_process.pack(side=LEFT, padx=5, pady=5)

        b_explore = Button(self.f_contract,
                           text = 'Explorer',
                           command = self._generate_contract)
        b_explore.pack(side=LEFT, padx=5, pady=5)

        b_cancel=Button(self.f_contract, text='Quitter', command=self.f_contract.quit)
        b_cancel.pack(side=RIGHT, padx=5, pady=5)

        self._gui_starting = False
        self._update_price()
    # end def _setup_contract

    def _get_calendar(self):
        if self._calendar is None:
            self._calendar = MejouCalendar(debug = self.debug)

            self._calendar.connect()
            self._calendar.parse_calendars()
        # end if
        return self._calendar
    # end def _get_calendar
    calendar = property(_get_calendar)

    def _setup_calendar(self):
        ''' Setup calendar GUI object '''
        font_title = '-family {DejaVu Sans} -size 14 -weight bold -overstrike 0'
        l_label = Label(self.f_calendar,
                       text = 'Calendrier du Mejou',
                       font = font_title)
        l_label.pack()

        self._print_rents()
    # end def _setup_calendar

    def _print_rents(self):
        ''' Print rent pricesmejourent '''
        rents = {}
        for gite in GITE_LIST:
            for rent in self.calendar.cal_mejou[gite]:
                mejou_rent_date = MejouRentDate(rent.start, rent.end)
                if mejou_rent_date in rents.keys():
                    rents[mejou_rent_date].append(rent)
                else:
                    rents[mejou_rent_date] = [rent]
                # end if
            # end for
        # end for

        l_title = TitleLabel(self.f_calendar)
        l_title.pack()

        for rent_date in sorted(list(rents.keys())):
            client_list = {r.client for r in rents[rent_date]}
            for client in client_list:

                rents_client = [rent for rent in rents[rent_date]
                                     if rent.client == client]

                l_rent = RentLabel(self.f_calendar,
                                   rents_client,
                                   self._validated_rent,
                                   self._cancel_rent)
                l_rent.pack()

                if rents_client[0].occupied:
                    str_occupied = 'Occupé'
                else:
                    str_occupied = 'Libre'
                # end if

                self.logger.log(f'{rent_date}: {rents_client[0].client} ({str_occupied})')
            # end for
        # end for
    # end def _print_rents

    def _validated_rent(self, client, start, end):
        self.calendar.validate_rent(client, start, end)
    # end def _validated_rent

    def _cancel_rent(self, client, start, end):
        self.calendar.cancel_rent(client, start, end)
    # end def _cancel_rent

    def _add_calendar(self, key, label, date = None):                                               #pylint: disable=redefined-outer-name
        ''' Add calendar GUI object '''
        parent = self.f_data

        l_label = Label(parent, text=label, width=25, anchor='w')
        l_label.grid(row=self.row, sticky='W')

        day, month, year = [int(field) for field in date.split('/')]

        calendar = Calendar(parent,
                            year = year,
                            month = month,
                            day = day,
                            locale = 'fr_fr',
                            date_pattern = 'd/m/y',
                            )
        calendar.grid(row=self.row, column=1, sticky='W')
        calendar.bind('<<CalendarSelected>>', self._update_cal)
        self.d_calendar[key] = calendar

        self.row += 1
    # end def _add_calendar

    def _add_radio(self, key, label, values):
        ''' Add Radio button object '''
        parent = self.f_data

        l_label = Label(parent, text=label, width=25, anchor='w')
        l_label.grid(row=self.row, sticky='W')

        var_gr = StringVar()
        var_gr.set(values[0])
        for val in values:
            radio_button = Radiobutton(parent,
                                       variable = var_gr,
                                       text     = val,
                                       value    = val,
                                       anchor   = 'w',
                                       width    = 25)
            radio_button.grid(row    = self.row,
                              column = 1,
                              sticky = 'W')
            self.row += 1
        # end for

        self.d_radio[key] = values[0]

        self.row += 1
    # end def _add_radio

    def _get_radio(self, key):
        ''' Getter for radio object '''
        return self.d_radio[key].get()
    # end def _get_radio
    def _set_radio(self, key, value):
        ''' Setter for radio object '''
        self.d_radio[key].set(value)
    # end def _set_radio

    def _get_titre(self):
        ''' Getter for 'titre' '''
        return self._get_radio('titre')
    # end def _get_titre
    def _set_titre(self, value):
        ''' Setter for 'titre' '''
        self.d_radio['titre'].set(value)
    # end def _set_titre

    def _add_price(self, key, label, value, update = True):
        text = price_to_str(value)
        self._add_text(key, label, text, update)
    # end def _add_price

    def _add_text(self, key, label, text, update = True):
        ''' Add text GUI object '''
        parent = self.f_data

        l_label = Label(parent, text=label, width=25, anchor='w')
        l_label.grid(row=self.row, sticky='W')

        s_var = StringVar()
        s_var.set(text)
        if update:
            s_var.trace('w', lambda name, index, mode, sv=s_var: self._update_price())              # @UnusedVariable pylint: disable=line-too-long
        # end if

        e_locataire = Entry(parent, textvariable=s_var, width=25)
        e_locataire.grid(row=self.row, column=1, sticky='W')

        self.d_text[key]  = s_var
        self.d_entry[key] = e_locataire

        self.row += 1
    # end def _add_text

    def _add_list(self, _key, label, value_list, _update = True):
        ''' Add dropbox list GUI object '''
        parent = self.f_data

        l_label = Label(parent, text=label, width=25, anchor='w')
        l_label.grid(row=self.row, sticky='W')

        s_var = StringVar(parent)
        s_var.set(value_list[0]) # default value

        o_menu = OptionMenu(parent, s_var, value_list)
        o_menu.grid(row=self.row, column=1, sticky='W')

        self.row += 1
    # end def _add_list

    def _lock_text(self, key, lock):
        ''' Lock given text object '''
        if lock:
            self.d_entry[key].config(state = constants.DISABLED)
        else:
            self.d_entry[key].config(state = constants.NORMAL)
        # end if
    # end def _lock_text

    def _get_text(self, key):
        ''' Getter for text object '''
        return self.d_text[key].get()
    # end def _get_text
    def _set_text(self, key, value):
        ''' Setter for text object '''
        self.d_text[key].set(value)
    # end def _set_text

    def _get_float(self, key):
        ''' Getter for numeric float object '''
        value = self.d_text[key].get()
        return str_to_price(value)
    # end def _get_float
    def _set_float(self, key, value):
        ''' Setter for numeric float object '''
        value = price_to_str(value)
        self._set_text(key, value)
    # end def _set_float

    def _get_date(self, key):
        ''' Getter for date objects '''
        return self.d_calendar[key].get_date()
    # end def _get_date
    def _set_date(self, key, value):
        ''' Setter for date objects '''
        self.d_calendar[key].set(value)
    # end def _set_date

    def _get_mr_mme(self):
        ''' Getter for mr/mme locataire '''
        return self._get_text('mr_mme')
    # end def _get_mr_mme
    def _set_mr_mme(self, mr_mme):
        ''' Setter for mr/mme locataire '''
        self._set_text('mr_mme', mr_mme)
    # end def _set_mr_mme
    _mr_mme = property(_get_mr_mme, _set_mr_mme)

    def _get_locataire(self):
        ''' Getter for locataire name '''
        return self._get_text('locataire')
    # end def _get_locataire
    def _set_locataire(self, locataire):
        ''' Setter for locataire name '''
        self._set_text('locataire', locataire)
    # end def _set_locataire
    _locataire = property(_get_locataire, _set_locataire)

    def _get_start(self):
        ''' Getter for start date '''
        start = self._get_date('start')
        return MejouDate.str_to_date(start,
                                   source = 'Début de location')
    # end def _get_start
    def _set_start(self, start):
        ''' Setter for start date '''
        self._set_date('start', MejouDate.short_date(start))
    # end def _set_start
    _start = property(_get_start, _set_start)

    def _get_end(self):
        end = self._get_date('end')
        return MejouDate.str_to_date(end,
                                     source = 'Fin de location')
    # end def _get_end
    def _set_end(self, end):
        self._set_date('end', MejouDate.short_date(end))
    # end def _set_end
    _end = property(_get_end, _set_end)

    def _get_price(self):
        price = self._get_float('price')
        if price == '':
            return 0
        # end if
        return int(price)
    # end def _get_price
    def _set_price(self, price):
        self._set_float('price', price)
    # end def _set_price
    _price = property(_get_price, _set_price)

    def _get_tax(self):
        return self._get_float('tax')
    # end def _get_tax
    def _set_tax(self, tax):
        self._set_float('tax', tax)
    # end def _set_tax
    _tax = property(_get_tax, _set_tax)

    def _get_taxyear(self):
        taxyear = self._get_text('taxyear')
        if taxyear == '':
            return 0
        # end if
        return float(taxyear.replace(',', '.'))
    # end def _get_taxyear
    def _set_taxyear(self, taxyear):
        self._set_text('taxyear', f'{taxyear}')
    # end def _set_taxyear
    _taxyear = property(_get_taxyear, _set_taxyear)

    def _get_sheets(self):
        return self._get_float('sheets')
    # end def _get_sheets
    def _set_sheets(self, sheets):
        self._set_float('sheets', f'{sheets}')
    # end def _set_sheets
    _sheets = property(_get_sheets, _set_sheets)

    def _get_towels(self):
        return self._get_float('towels')
    # end def _get_towels
    def _set_towels(self, towels):
        self._set_float('towels', f'{towels}')
    # end def _set_towels
    _towels = property(_get_towels, _set_towels)

    def _get_heating(self):
        return self._get_float('heating')
    # end def _get_heating
    def _set_heating(self, heating):
        self._set_float('heating', f'{heating}')
    # end def _set_heating
    _heating = property(_get_heating, _set_heating)

    def _get_beds(self):
        beds = self._get_text('beds')
        if beds == '':
            return 0
        # end if
        return int(beds)
    # end def _get_beds
    def _set_beds(self, beds):
        self._set_text('beds', f'{beds}')
    # end def _set_beds
    _beds = property(_get_beds, _set_beds)

    def _get_deposit(self):
        return self._get_float('deposit')
    # end def _get_deposit
    def _set_deposit(self, deposit):
        self._set_float('deposit', deposit)
    # end def _set_deposit
    _deposit = property(_get_deposit, _set_deposit)

    def _get_cleaning_price(self):
        price = self._get_float('cleaning')
        if price == '':
            return 0
        # end if
        return int(price)
    # end def _get_cleaning_price
    def _set_cleaning_price(self, price):
        self._set_float('cleaning', price)
    # end def _set_cleaning_price
    _cleaning = property(_get_cleaning_price, _set_cleaning_price)

    def _add_check(self, key, label, value, command = None):
        if command is None:
            command = self._update_price
        # end if

        parent = self.f_data

        if value not in (True, False):
            if value.lower() == 'true':
                value = 1
            else:
                value = 0
            # end if
        # end if
        bool_var = IntVar(value = value)

        checkbutton = Checkbutton(parent,
                                  text      = label,
                                  variable  = bool_var,
                                  width     = 30,
                                  anchor    = 'w',
                                  command   = command)
        checkbutton.grid(row=self.row, columnspan=2, sticky='W')

        self.d_check[key]       = bool_var
        self.d_check_button[key] = checkbutton

        self.row += 1
    # end def _add_check

    def _get_bool(self, key):
        '''
        Generic getter for reading boolean from check box
        @param key [in] (str) Key of the check box for self.d_check
        '''
        return self.d_check[key].get() == 1
    # end def _getKey
    def _set_bool(self, key, value):
        '''
        Generic setter for updating boolean from check box
        @param key   [in] (str) Key of the check box for self.d_check
        @param value [in] (bool) New value of the check box
        '''
        if value:
            value = 1
        else:
            value = 0
        # end if
        self.d_check[key].set(value)
    # end def _set_bool

    def _get_automatic(self):
        return self._get_bool('automatic')
    # end def _get_automatic
    def _set_automatic(self, value):
        self._set_bool('automatic', value)
    # end def _set_automatic
    _automatic = property(_get_automatic, _set_automatic)

    def _get_cleaning_inc(self):
        return self._get_bool('cleaninginc')
    # end def _get_cleaning_inc
    def _set_cleaning_inc(self, value):
        self._set_bool('cleaninginc', value)
    # end def _set_cleaning_inc
    _cleaning_inc = property(_get_cleaning_inc, _set_cleaning_inc)

    def _get_avelmor(self):
        return self._get_bool('avelmor')
    # end def _get_avelmor
    def _set_avelmor(self, value):
        self._set_bool('avelmor', value)
    # end def _set_avelmor
    _avelmor = property(_get_avelmor, _set_avelmor)

    def _get_tyagathe(self):
        return self._get_bool('tyagathe')
    # end def _get_tyagathe
    def _set_tyagathe(self, value):
        self._set_bool('tyagathe', value)
    # end def _set_tyagathe
    _tyagathe = property(_get_tyagathe, _set_tyagathe)

    def _get_typapy(self):
        return self._get_bool('typapy')
    # end def _get_typapy
    def _set_typapy(self, value):
        self._set_bool('typapy', value)
    # end def _set_typapy
    _typapy = property(_get_typapy, _set_typapy)

    def synch_data(self):
        ''' Synchronize data with Contract Manager '''
        self.cmgr.update_data(locataire      = self._locataire,
                              start           = self._start,
                              end             = self._end,
                              avelmor         = self._avelmor,
                              tyagathe        = self._tyagathe,
                              typapy          = self._typapy,
                              price           = self._price,
                              tax             = self._tax,
                              taxyear         = self._taxyear,
                              sheets          = self._sheets,
                              towels          = self._towels,
                              heating         = self._heating,
                              cleaning        = self._cleaning,
                              cleaning_inc    = self._cleaning_inc,
                              )
        self.cmgr.log_data()
    # end def synch_data

    def _update_cal(self, event):                                                                   # @UnusedVariable pylint: disable=unused-argument
        ''' @param event [in] (event) '''
        self._update_price()
    # end def _update_cal

    def _update_price(self):
        if self._gui_starting:
            return
        # end if

        self.synch_data()
        total_price, total_cleaning, total_beds, total_deposit = self.cmgr.get_total_price()

        #pylint: disable=multiple-statements
        if self._beds != total_beds: self._beds    = total_beds
        if self._deposit != total_deposit: self._deposit = total_deposit

        if self._automatic:
            if self._price != total_price: self._price = total_price
            if self._cleaning != total_cleaning: self._cleaning = total_cleaning
        # end if
        #pylint: enable=multiple-statements
    # end def _update_price

    def _switch_automatic(self):
        self._lock_text('price', self._automatic)
        self._lock_text('cleaning', self._automatic)
        self._update_price()
    # end def _switch_automatic

    @staticmethod
    def _open_explorer(path = None):
        args = ['explorer.exe', ]
        if isdir(path):
            args.append(path)
        elif isfile(path):
            args.append(f'/select,{path}')
        # end if
        Popen(args = args)
    # end def _open_explorer

    def _generate_contract(self):
        self.logger.log('Mise à jour des prix')
        self._update_price()

        for house in self.cmgr.house_list:
            self.calendar.add_rent(client = self._locataire,
                                   house  = house,
                                   start  = self._start,
                                   end    = self._end)
        # end for

        file_path = self.cmgr.create_pdf()
        self._save_config()
        self._open_explorer(file_path)
    # end def _generate_contract

    def clear_log(self):
        ''' Clear the log object '''
        if self.l_details is not None:
            self.l_details.delete(0, END)
        # end if
    # end def clear_log

    def log(self, msg):
        ''' Log the given message '''
        if self.l_details is not None:
            self.l_details.insert(END, msg)
        # end if
    # end def log

    @staticmethod
    def log_error(msg):
        ''' Log the given error message '''
        showerror(msg)
    # end def log_error
# end class ContractManagerGui


#===================================================================================================
# Main
#===================================================================================================

if __name__ == '__main__':
    cm = ContractManager()
    ContractManagerGui(cm)
# end if


#===================================================================================================
# End
#===================================================================================================
