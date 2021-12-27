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

from mejouseason                                    import INI_SEASONS
from mejouseason                                    import MejouSeason

#===================================================================================================
# Types
#===================================================================================================

class MejouHouse():                                                                                 #pylint: disable=too-many-instance-attributes, too-few-public-methods
    ''' Object for managing house properties '''
    def __init__(self,                                                                              #pylint: disable=too-many-arguments
                 name,
                 beds,
                 deposit,
                 night_cleaning,
                 night_low,
                 night_high,
                 week_cleaning,
                 week_low,
                 week_medium,
                 week_high,
                 week_very_high):
        ''' Constructor for house object '''
        self.name           = name
        self.beds           = beds
        self.deposit        = deposit

        self.night_cleaning  = night_cleaning
        self.night_low       = night_low
        self.night_high      = night_high

        self.week_cleaning   = week_cleaning
        self.week_low        = week_low
        self.week_medium     = week_medium
        self.week_high       = week_high
        self.week_very_high  = week_very_high
    # end def __init__

    def get_price(self, seasons, start, end):
        ''' Getter for price '''
        duration = (end-start).days
        if (duration > 7) and (duration % 7) != 0:
            raise NotImplementedError('Durée supérieure à 7 jours non implémentée')
        # end if

        found_season = None

        for season in seasons:
            if season.is_in_duration(start, end):
                found_season = season
                break
            # end if
        # end for

        if not found_season:
            raise ValueError(f'Saison non définie dans \'{INI_SEASONS}\' pour les dates du ' \
                             f'{start} au {end}')
        # end if

        if found_season.season_type == MejouSeason.LOW:
            result = self.week_low
        elif found_season.season_type == MejouSeason.MEDIUM:
            result = self.week_medium
        elif found_season.season_type == MejouSeason.HIGH:
            result = self.week_high
        elif found_season.season_type == MejouSeason.VERY_HIGH:
            result = self.week_very_high
        else:
            raise ValueError('Saison non trouvée')
        # end if

        return result
    # end def get_price
# end class MejouHouse


#===================================================================================================
# Main
#===================================================================================================


#===================================================================================================
# End
#===================================================================================================
