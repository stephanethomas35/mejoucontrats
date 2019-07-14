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

from datetime                                       import datetime
from datetools                                      import DateTools


#===================================================================================================
# Implementation
#===================================================================================================

class AbstractLogger(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self._debug = True
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
    def __init__(self):
        '''
        '''
        super(StdOutLogger, self).__init__()

        self.logFile = 'contrats.log'
    # end def __init__

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

        msg = '%s - %s' % (DateTools.isoDate(datetime.now()),
                           msg)
        with open(self.logFile, 'a') as f:
            f.write(msg)
        # end with
    # end def logError
# end class StdOutLogger


#===================================================================================================
# Main
#===================================================================================================


#===================================================================================================
# End
#===================================================================================================
