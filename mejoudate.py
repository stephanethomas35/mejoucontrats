# -*- coding: utf-8 -*-
#===================================================================================================
# @copyright Stéphane Thomas - 2018-2021
#
# Générateur de contrat pour Le Mejou - https://mejou.fr
#
#===================================================================================================

#===================================================================================================
# Imports
#===================================================================================================

from datetime                                       import date


#===================================================================================================
# Implementation
#===================================================================================================


class MejouDate():
    ''' Tools for managing/converting dates '''
    @staticmethod
    def str_to_date(str_date, source=''):
        ''' Convert the given string into date object '''
        if isinstance(str_date, date):
            return str_date
        # end if

        list_date = str_date.split('/')
        if len(list_date) != 3:
            print('La date n\'est pas au format \'jour/mois/année\'')
            print('Saisissez à nouveau !')

            raise ValueError('La date %s n\'est pas au format \'jour/mois/année\'' % source)
        # end if
        day, month, year = [int(i) for i in list_date]
        if year <= 99:
            year += 2000
        # end if
        return date(year, month, day)
    # end def str_to_date

    @staticmethod
    def iso_date(raw_date):
        ''' Convert date into string with ISO format ("YYYYmmdd") '''
        return raw_date.strftime('%Y%m%d')
    # end def iso_date

    @staticmethod
    def iso_date_time(raw_date):
        ''' Convert date into datetime '''
        return raw_date.strftime('%Y/%m/%d-%H:%M:%S')
    # end def iso_date_time

    @staticmethod
    def short_date(raw_date):
        ''' Convert date into short date string ("dd/mm/YYYY") '''
        return raw_date.strftime('%d/%m/%Y')
    # end def short_date

    @staticmethod
    def full_date(raw_date):
        ''' Convert date into full string '''
        return raw_date.strftime('%A %d %B %Y')
    # end def full_date
# end class MejouDate


#===================================================================================================
# Main
#===================================================================================================



#===================================================================================================
# End
#===================================================================================================
