# -*- coding: utf-8 -*-
#===================================================================================================
# @copyright Stéphane Thomas - 2018
#
# Générateur de contrat pour Le Mejou - http://mejou.fr
#
#===================================================================================================

# @TODO: supprimer Avel Mor des contrats sans Avel Mor
# @TODO: supprimer les lofts des contrats sans aucun loft

#===================================================================================================
# Imports
#===================================================================================================

from datetime                                       import date


#===================================================================================================
# Implementation
#===================================================================================================


class DateTools(object):
    '''
    '''
    @staticmethod
    def strToDate(strDate, source=''):
        '''
        '''
        if isinstance(strDate, date):
            return strDate
        # end if

        listDate = strDate.split('/')
        if len(listDate) != 3:
            print('La date n\'est pas au format \'jour/mois/année\'')
            print('Saisissez à nouveau !')

            raise ValueError('La date %s n\'est pas au format \'jour/mois/année\'' % source)
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


#===================================================================================================
# Main
#===================================================================================================



#===================================================================================================
# End
#===================================================================================================
