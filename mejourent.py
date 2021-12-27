# -*- coding: utf-8 -*-
'''
@copyright Stéphane Thomas - 2018-2021
Générateur de contrat pour Le Mejou - https://mejou.fr
'''

#===================================================================================================
# Standard Imports
#===================================================================================================


#===================================================================================================
# Third party Imports
#===================================================================================================

#===================================================================================================
# Personal Imports
#===================================================================================================


#===================================================================================================
# Types
#===================================================================================================

class MejouRentDate():
    ''' Class for managing rental dates '''
    def __init__(self, start, end):
        ''' Constructor '''
        self.start = start
        self.end = end
    # end def __init__

    def __str__(self):
        ''' String representation '''
        return f'{self.start.strftime("%d/%m/%Y")}-{self.end.strftime("%d/%m/%Y")}'
    # end def __str__

    def __repr__(self):
        ''' String representation '''
        return self.__str__()
    # end def __repr__

    def __hash__(self):
        ''' Object Hash '''
        return hash(self.__str__())
    # end def __hash__

    def __eq__(self, other):
        ''' Test equality '''
        return (self.start == other.start) and (self.end == other.end)
    # end def __eq__

    def __lt__(self, other):
        ''' Test lower than (<) '''
        if self.start < other.start:
            return True
        # end if
        if (self.start == other.start) and (self.end < other.end):
            return True
        # end if
        return False
    # end def __lt__
# end class MejouRentDate

class MejouRent():                                                                                  #pylint: disable=too-few-public-methods
    ''' Class defining Rent information '''
    def __init__(self, name, rent_date, available):
        ''' Constructor '''
        self.name      = name
        self.rent_date = rent_date
        self.available = available
    # end def __init__

    def __str__(self):
        ''' String representation '''
        txt = f'{self.rent_date.start}-{self.rent_date.end}: {self.name}'
        return txt
    # end def print
# end class MejouRent


#===================================================================================================
# Constants
#===================================================================================================


#===================================================================================================
# Implementation
#===================================================================================================


#===================================================================================================
# Main
#===================================================================================================


#===================================================================================================
# End
#===================================================================================================
