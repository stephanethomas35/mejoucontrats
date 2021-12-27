# -*- coding: utf-8 -*-
'''
@copyright Stéphane Thomas - 2018-2021
Générateur de contrat pour Le Mejou - https://mejou.fr
'''

#===================================================================================================
# Standard Imports
#===================================================================================================


#===================================================================================================
# Personal Imports
#===================================================================================================

from mejoudate                                      import MejouDate


#===================================================================================================
# Types
#===================================================================================================

class MejouSeason():
    '''
    Object for managing MejouSeason properties
    '''
    LOW         = 'Basse saison'
    MEDIUM      = 'Moyenne saison'
    HIGH        = 'Haute saison'
    VERY_HIGH   = 'Très haute saison'

    def __init__(self, name, start, end, season_type):
        '''
        Constructor
        '''
        self.name        = name
        self.start       = MejouDate.str_to_date(start)
        self.end         = MejouDate.str_to_date(end)
        self.season_type = season_type
    # end def __init__

    def __str__(self):
        ''' String representation '''
        return f'Du {self.start} au {self.end}: {self.season_type}'
    # end def __str__

    def is_in_duration(self, start, end):
        '''
        Return True if [start-end] period is part of current season
        '''
        if end < self.start:
            return False
        if start >= self.end:
            return False
        if (start >= self.start) and (end <= self.end):
            return True

        raise NotImplementedError(f'Périodes [{start}->{end}] partiellement dans la saison: ' \
                                  f'{self.name} [{self.start}->{self.end}]')
    # end def is_in_duration
# end class MejouSeason


#===================================================================================================
# Constants
#===================================================================================================

INI_SEASONS = 'mejousaisons.ini'

SEASON_TYPE = {'basse':      MejouSeason.LOW,
               'moyenne':    MejouSeason.MEDIUM,
               'haute':      MejouSeason.HIGH,
               'tres haute': MejouSeason.VERY_HIGH,
               }


#===================================================================================================
# Main
#===================================================================================================


#===================================================================================================
# End
#===================================================================================================
