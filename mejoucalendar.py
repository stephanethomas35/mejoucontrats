# -*- coding: utf-8 -*-
'''
@copyright Stéphane Thomas - 2018-2021
Générateur de contrat pour Le Mejou - https://mejou.fr

From https://developers.google.com/calendar/quickstart/python
'''

# --------------------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------------------

import calendar
import datetime
import os
import pickle
import webbrowser
from tkinter.messagebox                 import askyesno

from dominate                           import document
from dominate                           import tags
from google.auth.transport.requests     import Request
from google_auth_oauthlib.flow          import InstalledAppFlow
from googleapiclient.discovery          import build

from mejouconst                         import GITE_LIST

# --------------------------------------------------------------------------------------------------
# Implementation
# --------------------------------------------------------------------------------------------------

WIDTH_DAY = 3

class COL:  #pylint: disable=too-few-public-methods
    '''
    Escape codes for coloring text in console
    '''
    BOLD      = '\033[1m'
    ENDC      = '\033[0m'
    FAIL      = '\033[91m'
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKCYAN    = '\033[96m'
    OKGREEN   = '\033[92m'
    UNDERLINE = '\033[4m'
    WARNING   = '\033[93m'
# end class COL

MONTH = {1: 'Janvier',
         2: 'Février',
         3: 'Mars',
         4: 'Avril',
         5: 'Mai',
         6: 'Juin',
         7: 'Juillet',
         8: 'Août',
         9: 'Septembre',
         10:'Octobre',
         11:'Novembre',
         12:'Décembre',
         }

OFFSET = {0: 2, # Monday
          1: 3, # Tuesday
          2: 4, # Wednesday
          3: 5, # Thursday
          4: 6, # Friday
          5: 0, # Saturday
          6: 1, # Sunday
          }

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ['https://www.googleapis.com/auth/calendar']

class Rent():                                                                                       #pylint: disable=too-few-public-methods
    '''
    Class representing a renmejourent
    '''
    def __init__(self, cal_id, event_id, start, end, client, house, occupied):                      #pylint: disable=too-many-arguments
        ''' Constructor '''
        self.cal_id   = cal_id
        self.event_id = event_id
        self.start    = start
        self.end      = end
        self.client   = client
        self.house    = house
        self.occupied = occupied
    # end __init__

    def __str__(self):
        ''' String representation '''
        return f'{self.event_id} - {self.house} - {self.client} [{self.start}-{self.end}]'
    # end def __str__

    def __repr__(self):
        ''' Debug representation '''
        return self.__str__()
    # end def __repr__
# end class


class MejouCalendar():                                                                              #pylint: disable=too-many-instance-attributes
    '''
    Class for managing Calendar of Mejou
    '''
    def __init__(self, debug = False):
        '''
        Class constructor
        '''
        self.debug = debug

        self.service        = None
        self._calendar_list = None

        self.date_min = datetime.date(2100, 12, 31)
        self.date_max = datetime.date(1970, 1, 1)

        self.cal_mejou = {}
        for gite in GITE_LIST:
            self.cal_mejou[gite] = []
        # end for

        self.title_len = max([len(gite) for gite in GITE_LIST] \
                             + [5 + len(month) for month in MONTH.values()])
    # end def

    def _print_debug(self, msg):
        '''
        Print message if debug mode is on
        '''
        if self.debug:
            print(msg)
        # end if
    # end def _print_debug

    def _print_underlined(self, msg):
        '''
        Print message with line of same size on next line
        @param [in] (str) Message to be printed
        '''
        self._print_debug('')
        self._print_debug(msg)
        self._print_debug('-' * len(msg))
    # end def _print_underlined

    def connect(self):
        '''
        Connect to Google Calendar service
        Client ID: 82124876902-ro1uqh0vfupnbj30qnp8ff4tkmt13vnd.apps.googleusercontent.com
        Client Secret:  iFcrjA4wlB9K10CyncK6xErJ

        Set (ressource object) into service attribute
        '''
        creds = None

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
            # end with
        # end if

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # end if

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
            # end with
        # end if

        self.service = build(serviceName = 'calendar',
                             version     = 'v3',
                             credentials = creds)
    # end def connect

    def _get_next_events(self, item):                                                                #pylint: disable=too-many-locals
        '''
        Get the next event from current calendar item
        '''
        gite = item['summary']

        now  = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

        # Call the Calendar API
        result = self.service.events().list(calendarId   = item['id'],                              #pylint: disable=no-member
                                            timeMin      = now,
                                            singleEvents = True,
                                            orderBy      = 'startTime').execute()
        events = result.get('items', [])

        import pprint
        pprint.pprint(events)

        for event in events:
            self._print_debug(f'calendarid={item["id"]} ({item["summary"]}) ' \
                              f'- eventid={event["id"]} ({event["summary"]})')
            start = event['start'].get('dateTime', event['start'].get('date'))
            end   = event['end'].get('dateTime', event['end'].get('date'))

            client = event['summary']

            start_year, start_month, start_day = start.split('-')
            start_day = start_day.split('T')[0]
            start_date = datetime.date(int(start_year),
                                       int(start_month),
                                       int(start_day))
            self.date_min = min(self.date_min, start_date)

            end = event['end'].get('dateTime', event['end'].get('date'))
            end_year, end_month, end_day = end.split('-')
            end_day = end_day.split('T')[0]
            end_date = datetime.date(int(end_year),
                                     int(end_month),
                                     int(end_day))
            self.date_max = max(self.date_max, end_date)

            available = ('transparency' in event.keys()) \
                        and (event['transparency'] == 'transparent')
            self.cal_mejou[gite].append(Rent(cal_id   = item["id"],
                                             event_id = event['id'],
                                             start    = start_date,
                                             end      = end_date,
                                             client   = client,
                                             house    = item['summary'],
                                             occupied = (not available)))

        # end for
    # end def _get_next_events

    def _is_occupied(self, gite, date):
        '''
        Return true if the given gite is occupied at the given date
        '''
        if date is None:
            return False
        # end if

        result = False
        for rent in self.cal_mejou[gite]:
            if rent.start <= date <= rent.end:
                result = True
                break
            # end if
        # end for
        return result
    # end def _is_occupied

    def _get_calendar_list(self):
        if self._calendar_list is None:
            self._calendar_list = self.service.calendarList().list().execute()                      #pylint: disable=no-member
        # end if
        return self._calendar_list
    # end def _get_calendar_list
    calendar_list = property(_get_calendar_list)

    def parse_calendars(self):
        '''
        Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        '''
        gite_items = [item for item in self.calendar_list['items']
                           if item['summary'] in GITE_LIST]

        for item in gite_items:
            self._get_next_events(item)
        # end for
    # end def parse_calendars

    def _get_rent_list(self, client, start, end):
        rent_list = []
        for cal_rents in self.cal_mejou.values():
            rent_list.extend(cal_rents)
        # end for

        start = datetime.datetime.strptime(start, '%d/%m/%y').date()
        end   = datetime.datetime.strptime(end,   '%d/%m/%y').date()

        rent_list = [rent for rent in rent_list
                     if (rent.client == client) and (rent.start == start) and (rent.end == end)]
        self._print_debug(rent_list)

        return rent_list
    # end def _get_rent_list

    def _get_cal_id(self, house):
        cal_list = [cal for cal in self.calendar_list['items']
                        if cal['summary'] == house]
        assert len(cal_list) <= 1

        if len(cal_list) == 0:
            cal_id = None
        else:
            cal_id = cal_list[0]['id']
        # end if

        return cal_id
    # end def _get_cal_id

    def add_rent(self, client, house, start, end):
        ''' Add the rent to the calendar with the given client and dates '''
        self._print_debug(f'Ajout de {client} ({house}) [{start}-{end}]...')
        cal_id = self._get_cal_id(house)

        event = {
          'summary': client,
          'start':   {'date': start.strftime('%Y-%m-%d')},
          'end':     {'date': end.strftime('%Y-%m-%d')},
          'transparency': 'transparent',
        }

        _updated_event = self.service.events().insert(calendarId = cal_id,                          #pylint: disable=no-member
                                                      body       = event).execute()
        self._print_debug(f'Ajout de {client} ({house}) [{start}-{end}] Done!')
    # end def add_rent

    def validate_rent(self, client, start, end):
        ''' Validate the rent with the given client and dates '''
        self._print_debug(f'Validate {client} [{start}-{end}]')
        rents = self._get_rent_list(client, start, end)

        for rent in rents:
            event = self.service.events().get(calendarId = rent.cal_id,                             #pylint: disable=no-member
                                              eventId    = rent.event_id).execute()

            if ('transparency' not in event.keys()) or (event['transparency'] != 'transparent'):
                continue
            # end if

            del event['transparency']

            _updated_event = self.service.events().update(calendarId = rent.cal_id,                  #pylint: disable=no-member
                                                         eventId    = rent.event_id,
                                                         body       = event).execute()
            # # Sanity check: test all values except 'updated' and 'etag'
            # assert event == updated_event
        # end for
        self._print_debug(f'Validate {client} [{start}-{end}]. Done!')
    # end def validate_rent

    def cancel_rent(self, client, start, end):
        ''' Delete the rent with the given client and dates '''
        answer = askyesno(title='Confirmation',
                          message = f'Confirmer la suppression de la location de {client} ' \
                                    f'du {start} au {end} ?')
        if not answer:
            return
        # end if

        self._print_debug(f'Cancel {client} [{start}-{end}]. Starting...')
        rents = self._get_rent_list(client, start, end)

        for rent in rents:
            self.service.events().delete(calendarId = rent.cal_id,                                  #pylint: disable=no-member
                                         eventId    = rent.event_id,
                                         ).execute()
        # end for
        self._print_debug(f'Cancel {client} [{start}-{end}]. Done!')
    # end def cancel_rent

    def print_calendar_list(self):
        '''
        Print the Calendar summary in stdout
        '''
        for gite in GITE_LIST:
            self._print_underlined(f'Gite = {gite}')
            if self.cal_mejou[gite] == []:
                self._print_debug('No upcoming events found.')
            # end if
            for rent in self.cal_mejou[gite]:
                self._print_debug(f'{rent.start}/{rent.end} {rent.client} ({rent.occupied})')
                if not rent.occupied:
                    self._print_debug('  ===> Logement non occupé, mettre à jour le calendrier')
                # end if
            # end for
        # end for

        self._print_debug('')
        self._print_debug('')
    # end def print_calendar_list

    def _print_separator(self):
        '''
        Print separator line
        '''
        lbar = f'{"-":-<{7*WIDTH_DAY}}'
        titlen = self.title_len + 2
        self._print_debug(f'+{"-":-<{titlen}}+{lbar}+{lbar}+{lbar}+{lbar}+{lbar}+{lbar}+')
    # end def _print_separator

    def _print_cal_days(self):
        '''
        Print the line with week days
        '''
        w = WIDTH_DAY                                                                               #pylint: disable=invalid-name
        week = f'{"S":>{w}}{"D":>{w}}{"L":>{w}}{"M":>{w}}{"M":>{w}}{"J":>{w}}{"V":>{w}}'
        self._print_debug(f'| {" ": <{self.title_len}} |{week}|{week}|{week}|{week}|{week}|{week}|')
    # end def _print_cal_days

    @staticmethod
    def _getday_num(year, month, week, day):
        '''
        Get the day number of the given date
        '''
        day_max = calendar.monthrange(year, month)[1]

        week_1st_day = datetime.date(year, month, 1).weekday()
        offset = OFFSET[week_1st_day]

        day_num = week*7 - offset + day
        if (day_num < 0) or (day_num >= day_max):
            day_num = None
        else:
            day_num += 1
        # end if

        return day_num
    # end def _getday_num

    def _get_week_block(self, year, month, week):
        '''
        Get the week block
        '''
        week_block = ''

        for day in range(7):
            day_num = self._getday_num(year, month, week, day)
            if day_num is None:
                week_block += ' ' * WIDTH_DAY
            else:
                week_block += f'{day_num: >{WIDTH_DAY}}'
            # end if
        # end for

        return week_block
    # end def _get_week_block

    def __print_month_line(self, year, month):
        '''
        Print a month line
        '''
        month_str = f'{MONTH[month]} {year}'

        w1 = self._get_week_block(year, month, 0)                                                    #pylint: disable=invalid-name
        w2 = self._get_week_block(year, month, 1)                                                    #pylint: disable=invalid-name
        w3 = self._get_week_block(year, month, 2)                                                    #pylint: disable=invalid-name
        w4 = self._get_week_block(year, month, 3)                                                    #pylint: disable=invalid-name
        w5 = self._get_week_block(year, month, 4)                                                    #pylint: disable=invalid-name
        w6 = self._get_week_block(year, month, 5)                                                    #pylint: disable=invalid-name

        self._print_debug(f'| {month_str: <{self.title_len}} |{w1}|{w2}|{w3}|{w4}|{w5}|{w6}|')
    # end def __print_month_line

    def _print_cal_line(self, gite, year, month):
        '''
        Print the given calendar line for the given gite
        '''
        week = {}
        for w in range(6):                                                                          #pylint: disable=invalid-name
            line = ''
            for day in range(7):
                date = None

                day_num = self._getday_num(year, month, w, day)
                if day_num is not None:
                    date = datetime.date(year, month, day_num)
                # end if

                if not self._is_occupied(gite, date):
                    line += ' ' * WIDTH_DAY
                else:
                    line += f'{"X":>{WIDTH_DAY}}'
                # end if
            # end for
            week[w] = line
        # end for

        self._print_debug(f'| {gite: <{self.title_len}} ' \
                          f'|{week[0]}|{week[1]}'
                          f'|{week[2]}|{week[3]}'
                          f'|{week[4]}|{week[5]}|')
    # end def _print_cal_line

    def _print_month(self, year, month):
        '''
        Print given month text
        '''
        self.__print_month_line(year, month)
        self._print_separator()
        for gite in GITE_LIST:
            self._print_cal_line(gite, year, month)
        # end for
        self._print_separator()
    # end def _print_month

    def print_calendar_table(self):
        '''
        Print the text calendar
        '''
        self._print_separator()
        self._print_cal_days()
        self._print_separator()

        for year, month in self._month_iter(self.date_min.year, self.date_min.month,
                                            self.date_max.year, self.date_max.month+1):
            self._print_month(year, month)
        # end for
    # end def print_calendar_table

    @staticmethod
    def _build_header_line():
        '''
        Build header line
        '''
        lheader = tags.tr()
        lheader += tags.th(' ')
        for _week in range(6):
            for day in ('S', 'D', 'L', 'M', 'M', 'J', 'V'):
                lheader += tags.th(day)
            # end for
        # end for
    # end def _build_header_line

    def _build_month_line(self, year, month):
        '''
        Build a line with month name
        '''
        lmonth = tags.tr()
        lmonth += tags.th(f'{MONTH[month]} {year}')
        for week in range(6):
            for day in range(7):
                day_num = self._getday_num(year, month, week, day)
                if day_num is None:
                    cell = ' '
                else:
                    cell = day_num
                # end if
                lmonth += tags.th(cell)
            # end for
        # end for
    # end _build_month_line

    def _build_gite_line(self, gite, year, month):
        '''
        Build a line with gite name
        '''
        giteid = gite.replace(' ', '').replace('+', '').lower()
        lgite = tags.tr(id=giteid)
        lgite += tags.td(gite)

        for week in range(6):
            for day in range(7):
                date = None
                day_num = self._getday_num(year, month, week, day)
                if day_num is not None:
                    date = datetime.date(year, month, day_num)
                # end if

                if self._is_occupied(gite, date):
                    cell = f'{COL.FAIL}X{COL.ENDC}'
                else:
                    cell = ' '
                # end if
                lgite += tags.td(cell)
            # end for
        # end for
    # end _build_gite_line

    @staticmethod
    def _month_iter(start_year, start_month, end_year, end_month):
        '''
        Iterator on month
        '''
        ym_start = 12*start_year + start_month - 1
        ym_end   = 12*end_year + end_month - 1
        for ym in range(ym_start, ym_end):                                                          #pylint: disable=invalid-name
            y, m = divmod(ym, 12)                                                                   #pylint: disable=invalid-name
            yield y, m+1
        # end for
    # end def _month_iter

    def build_html(self):
        '''
        Build the HTML Calendar
        '''
        doc = document(title='Calendrier Mejou')

#             tr:nth-child(odd)  {background: #b8d1f3 }
#             tr:nth-child(even) {background: #dae5f4 }

        with doc.head:
            tags.style('''
            body { font-family: Arial, sans-serif;}
            table { border-collapse: collapse; }
            td { min-width: 1em; }
            table, th, td { border: 1px solid ; }
            tr#avelmor { background: MistyRose }
            tr#tyagathe { background: lightblue }
            tr#tytania { background: LightGreen }
            tr#typapy { background: Orange }
            tr#tyagathetytania { background: LightYellow }
            th { font-weight: bold;
                 color: white;
                 background: Blue; }
            td:nth-child(7n+2) { border-left: 3px solid Black }
            ''')
        # end with

        with doc.body:
            tags.h1('Calendrier Mejou')
            tags.h2(f'du {self.date_min.strftime("%d/%m/%Y")} au {self.date_max.strftime("%d/%m/%Y")}')  #pylint: disable=line-too-long

            with tags.table().add(tags.tbody()):
                self._build_header_line()

                for year, month in self._month_iter(self.date_min.year, self.date_min.month,
                                                    self.date_max.year, self.date_max.month+1):
                    self._build_month_line(year, month)
                    for gite in GITE_LIST:
                        self._build_gite_line(gite, year, month)
                # end for
            # end with
        # end with


#         html_name = 'calendar.html'
#         with open(html_name, 'w') as html_file:
#             html_file.write(doc.render(pretty=True))
#         # end with
#
#         import webbrowser
#         webbrowser.open_new_tab(html_name)

        html = '''<!DOCTYPE html>
<html>
  <head>
    <title>Calendrier Mejou</title>
    <style>
            body { font-family: Arial, sans-serif;}
            table { border-collapse: collapse; }
            td { min-width: 1em; }
            table, th, td { border: 1px solid ; }
            tr#avelmor { background: MistyRose }
            tr#tyagathe { background: lightblue }
            tr#tytania { background: LightGreen }
            tr#typapy { background: Orange }
            tr#tyagathetytania { background: LightYellow }
            th { font-weight: bold;
                 color: white;
                 background: Blue; }
            td:nth-child(7n+2) { border-left: 3px solid Black }
            </style>
  </head>
  <body>
    <h1>Calendrier Mejou</h1>
    <h2>du 23/12/2020 au 27/06/2021</h2>
  </body>
</html>'''


        cal_name = 'hcal.html'
        with open(cal_name, mode='w', encoding='utf-8') as cal_file:
            cal_file.write(html)
        # end with

        webbrowser.open_new_tab(cal_name)
    # end def build_html
# end class MejouCalendar


# --------------------------------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    cal = MejouCalendar(debug = True)

    cal.connect()
    cal.parse_calendars()
    cal.print_calendar_list()
    cal.print_calendar_table()
    cal.build_html()
# end if


# --------------------------------------------------------------------------------------------------
# END
# --------------------------------------------------------------------------------------------------
