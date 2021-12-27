# -*- coding: utf-8 -*-
'''
@copyright Stéphane Thomas - 2018-2021
Générateur de contrat pour Le Mejou - https://mejou.fr
'''

#===================================================================================================
# Standard Imports
#===================================================================================================

from configparser                                   import RawConfigParser
from datetime                                       import timedelta
import locale

#===================================================================================================
# Personal Imports
#===================================================================================================

from mejouconst                                     import AVEL_MOR
from mejouconst                                     import INI_GITES
from mejouconst                                     import TY_AGATHE
from mejouconst                                     import TY_PAPY
from mejoudate                                      import MejouDate
from mejouhouse                                     import MejouHouse
from mejoulogger                                    import StdOutLogger
from mejoupdf                                       import Contract2Pdf
from mejouseason                                    import INI_SEASONS
from mejouseason                                    import MejouSeason
from mejouseason                                    import SEASON_TYPE


#===================================================================================================
# Types
#===================================================================================================


#===================================================================================================
# Constants
#===================================================================================================


#===================================================================================================
# Implementation
#===================================================================================================

class ContractManager():                                                                            #pylint: disable=too-many-instance-attributes
    '''
    Contract manager - manage the input and generate the contract
    '''
    def __init__(self, basedir = None):
        '''
        Contract manager constructor
        @option basedir [in] (str) Directory where the
        '''
        locale.setlocale(locale.LC_ALL,'')
        self.logger         = StdOutLogger()

        if basedir is None:
            basedir = 'contrats'
        # end if
        self._basedir       = basedir

        self._locataire     = None

        self._avelmor       = True
        self._tyagathe      = True
        self._typapy        = True

        self._start         = None
        self._end           = None

        self._ratio         = 25
        self._price         = None
        self._tax           = None
        self._taxyear       = None
        self._sheets        = None
        self._towels        = None
        self._heating       = None
        self._cleaning      = 0
        self._cleaning_inc  = None
        self._beds          = None
        self._deposit       = None

        self._seasons       = self._read_seasons()
        self._houses        = self._read_houses()
    # end def __init__

    @staticmethod
    def _read_seasons():
        ''' Read the seasons from the config file '''
        parser = RawConfigParser()
        parser.read(INI_SEASONS)

        seasons = []

        for section in parser.sections():
            season_start = parser.get(section, 'debut')
            season_end   = parser.get(section, 'fin')
            season_type  = parser.get(section, 'type')

            try:
                season_type = SEASON_TYPE[season_type.lower()]
            except KeyError:
                raise ValueError(f'Type de saison incorrecte: {season_type}') from KeyError
            # end if

            seasons.append(MejouSeason(name        = section,
                                       start       = season_start,
                                       end         = season_end,
                                       season_type = season_type))
        # end for

        return seasons
    # end def _read_seasons

    @staticmethod
    def _read_houses():
        ''' Read the houses from the config file '''
        parser = RawConfigParser()
        parser.read(INI_GITES)

        houses = {}

        for name in parser.sections():
            beds            = parser.get(name, 'lits')
            deposit         = parser.get(name, 'caution')

            night_cleaning  = parser.get(name, 'nuit_menage')
            night_low       = parser.get(name, 'nuit_basse')
            night_high      = parser.get(name, 'nuit_moyenne')

            week_cleaning   = parser.get(name, 'semaine_menage')
            week_low        = parser.get(name, 'semaine_basse')
            week_medium     = parser.get(name, 'semaine_moyenne')
            week_high       = parser.get(name, 'semaine_haute')
            week_very_high  = parser.get(name, 'semaine_t_haute')

            houses[name]= MejouHouse(name           = name,
                                     beds           = int(beds),
                                     deposit        = int(deposit),
                                     night_cleaning = int(night_cleaning),
                                     night_low      = int(night_low),
                                     night_high     = int(night_high),
                                     week_cleaning  = int(week_cleaning),
                                     week_low       = int(week_low),
                                     week_medium    = int(week_medium),
                                     week_high      = int(week_high),
                                     week_very_high = int(week_very_high))
        # end for

        return houses
    # end def _read_houses

    def _get_duration(self):
        return (self._end - self._start).days
    # end _get_duration
    _duration = property(_get_duration)

    def _get_house_list(self):
        house_list = []

        if self._avelmor:
            house_list.append(AVEL_MOR)
        if self._tyagathe:
            house_list.append(TY_AGATHE)
        if self._typapy:
            house_list.append(TY_PAPY)

        return house_list
    # end def _get_house_list
    house_list = property(_get_house_list)

    def _get_season(self, start, end):
        for season in self._seasons:
            if (MejouDate.str_to_date(start) >= MejouDate.str_to_date(season.start)) \
                and (MejouDate.str_to_date(end) <= MejouDate.str_to_date(season.end)):

                return season.season_type
            # end if
        # end for
        raise ValueError(f'Saison non définie pour la période du {start} au {end}')
    # end def _get_season

    def _get_house_price(self, house_name, week_list):
        '''
        '''
        total_price    = 0
        total_cleaning = 0

        for start, end in week_list:
            duration = (end - start).days
            assert 0 < duration <= 7

            house       = self._houses[house_name]
            price_week  = house.get_price(self._seasons, start, end)
            price_night = house.night_low

            price_per_night = self._duration*price_night
            if (duration == 7) or (price_per_night > price_week):
                # Duration = a week or price for a week is smaller
                house_price = price_week
                cleaning    = house.week_cleaning
            else:
                # Price
                house_price = price_per_night
                cleaning    = house.night_cleaning
            # end if

            self.logger.log(f'Prix pour {house_name} ({MejouDate.short_date(start)} ' \
                            f'au {MejouDate.short_date(end)}):  {house_price} Euros')

            total_price += house_price
            total_cleaning += cleaning
        # end for

        self.logger.log(f'Ménage pour {house_name} : {cleaning} Euros')

        add_text = ''
        if self._cleaning_inc:
            total_price += total_cleaning
            add_text = ' (ménage inclus)'
        # end if
        self.logger.log(f'Total pour {house_name} : {total_price} Euros {add_text}')
        return (total_price, total_cleaning)
    # end def _get_house_price

    def get_total_price(self):
        '''
        Get the total price of the renting
        '''
        week_list = []
        if self._duration <= 7:
            week_list.append([self._start, self._end])
        else:
            start = self._start
            end = self._start + timedelta(7)

            while start < self._end:
                week_list.append([start, end])
                start += timedelta(7)
                end += timedelta(7)
                if end > self._end:
                    end = self._end
                # end if
            # end while
        # end if

        total_price    = 0
        total_cleaning = 0
        for house in self.house_list:
            price, cleaning = self._get_house_price(house, week_list)
            total_price += price
            total_cleaning += cleaning
        # end for

        self._beds    = sum([self._houses[house].beds    for house in self.house_list])
        self._deposit = sum([self._houses[house].deposit for house in self.house_list])

        return total_price, total_cleaning, self._beds, self._deposit
    # end def get_total_price

    def _count_houses(self):
        return len(self.house_list)
    # end def _count_houses

    def update_data(self, locataire,                                                                #pylint: disable=too-many-arguments
                          start,
                          end,
                          avelmor,
                          tyagathe,
                          typapy,
                          price,
                          tax,
                          taxyear,
                          sheets,
                          towels,
                          heating,
                          cleaning,
                          cleaning_inc):
        '''
        Update data from given parameters
        '''
        self._locataire     = locataire
        self._start         = start
        self._end           = end

        self._avelmor       = avelmor
        self._tyagathe      = tyagathe
        self._typapy        = typapy

        self._price         = 0 if price=='' else int(price)
        self._tax           = tax
        self._taxyear       = taxyear
        self._sheets        = sheets
        self._towels        = towels
        self._heating       = heating
        self._cleaning      = 0 if cleaning==''  else int(cleaning)
        self._cleaning_inc  = cleaning_inc
    # end def update_data

    def log_data(self):
        '''
        Log current data
        '''
        self.logger.clear_log()
        if self._cleaning_inc:
            self.logger.log('Ménage inclus')
        else:
            self.logger.log('Ménage en sus')
        # end if
    # end def log_data

    def create_pdf(self):
        '''
        Generate the PDF contract file
        @return (str) Path to PDF File, or ODT file if not PDF File was created
        '''
        c2p = Contract2Pdf(locataire    = self._locataire,
                           avelmor      = self._avelmor,
                           tyagathe     = self._tyagathe,
                           typapy       = self._typapy,
                           start        = self._start,
                           end          = self._end,
                           ratio        = self._ratio,
                           price        = self._price,
                           tax          = self._tax,
                           sheets       = self._sheets,
                           towels       = self._towels,
                           heating      = self._heating,
                           cleaning     = self._cleaning,
                           cleaning_inc = self._cleaning_inc,
                           beds         = self._beds,
                           deposit      = self._deposit,
                           house_list   = self.house_list,
                           basedir      = self._basedir)
        return c2p.create_pdf()
# end class ContractManager


#===================================================================================================
# Main
#===================================================================================================


#===================================================================================================
# End
#===================================================================================================
