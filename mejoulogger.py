# -*- coding: utf-8 -*-
'''
@copyright Stéphane Thomas - 2018-2021
Générateur de contrat pour Le Mejou - https://mejou.fr
'''

#===================================================================================================
# Imports
#===================================================================================================

from datetime                                       import datetime
from mejoudate                                      import MejouDate


#===================================================================================================
# Implementation
#===================================================================================================

class AbstractLogger():
    '''
    Abstract logger
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self._debug = True
    # end def __init__

    def clear_log(self):
        '''
        Clear the log object
        '''
        raise NotImplementedError
    # end def clear_log

    def log(self, msg):
        '''
        Log the given message
        '''
        raise NotImplementedError
    # end def log

    def log_error(self, msg):
        '''
        Log the Error message
        '''
        raise NotImplementedError
    # end def log_error

    def log_dbg(self, msg):
        '''
        Log the Debug message
        '''
        if self._debug:
            self.log(msg)
        # end if
    # end def log_dbg
# end class AbstractLogger

class StdOutLogger(AbstractLogger):
    ''' Logger on stdout '''
    def __init__(self):
        '''
        '''
        super().__init__()

        self.log_file = 'mejmejouguig'
    # end def __init__

    def clear_log(self):
        ''' Clear log '''
    # end def clear_log

    def log(self, msg):
        ''' Log given message '''
        print(msg)
    # end def log

    def log_error(self, msg):
        ''' Log given error message '''
        print(msg)

        msg = '%s - %s\n' % (MejouDate.iso_date_time(datetime.now()),
                           msg)
        with open(self.log_file, mode='a', encoding='utf-8') as out_file:
            out_file.write(msg)
        # end with
    # end def log_error
# end class StdOutLogger


#===================================================================================================
# Main
#===================================================================================================


#===================================================================================================
# End
#===================================================================================================
