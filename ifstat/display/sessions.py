import curses
from itertools import islice, izip

from .rate import get_rate_string

SESSIONS_HEADER = "| Idx | Type | Details                                         | RX Rate        | TX Rate        | Time              "
SESSIONS_BORDER = "+-----+------+-------------------------------------------------+----------------+----------------+-------------------"
EMPTY_LINE = "|     |      |                                                 |                |                |                   "
PAD_X_SIZE = len(SESSIONS_HEADER) + 1
HEADER_LINES = 3
FOOTER_LINES = 1
EXTRA_LINES = HEADER_LINES + FOOTER_LINES

def _get_time_string(time_seconds):
    return "%02d:%02d:%02d" % (int(time_seconds / 60 / 60),
                               int(time_seconds / 60),
                               int(time_seconds) % 60)

SORT_KEYS = {'r': ('rx_bps', True),
             'R': ('rx_bps', False),
             't': ('tx_bps', True),
             'T': ('tx_bps', False),
             's': ('source_ip', True),
             'S': ('source_ip', False),
             'p': ('source_port', True),
             'P': ('source_port', False),
             'd': ('dest_ip', True),
             'D': ('dest_ip', False),
             '{': ('dest_port', True),
             '[': ('dest_port', False),
             'l': ('time', True),
             'L': ('time', False),
             'k': ('key', True),
             'K': ('key', False),
            }
SORT_KEYS_ORDINALS = [ord(key) for key in SORT_KEYS]

class SessionsPad(object):
    def __init__(self, sessions_number=20, ylocation=0, xlocation=0, colors=None):
        self._sessions_number = sessions_number
        self._ylocation = ylocation
        self._xlocation = xlocation
        self._colors = colors
        self._top_line = 0
        self._pad = curses.newpad(self._sessions_number + EXTRA_LINES, PAD_X_SIZE)
        self._pad.addstr(0, 0, SESSIONS_BORDER)
        self._pad.addstr(1, 0, SESSIONS_HEADER)
        self._pad.addstr(2, 0, SESSIONS_BORDER)
        self._pad.addstr(HEADER_LINES + self._sessions_number, 0, SESSIONS_BORDER)
        self._sort_by = 'key'
        self._sort_reverse = True

    def key(self, key):
        if key == curses.KEY_DOWN:
            if self._top_line < self._sessions_number:
                self._top_line += 1
            return

        if key == curses.KEY_UP:
            self._top_line -= 1
            if self._top_line < 0:
                self._top_line = 0
            return

        if key in SORT_KEYS_ORDINALS:
            key = chr(key)
            self._sort_by, self._sort_reverse = SORT_KEYS[key]
            return

    def get_y_size(self):
        return EXTRA_LINES + self._sessions_number

    def get_x_size(self):
        return PAD_X_SIZE

    def _get_session_color(self, session):
        if self._colors is None:
            return 0

        if session.is_new:
            return curses.color_pair(self._colors["green"])
        if session.is_dead:
            return curses.color_pair(self._colors["red"])

        return 0

    def display(self, sessions):
        if len(sessions) <= self._sessions_number:
            self._top_line = 0
        
        sessions.sort(key=lambda x: getattr(x, self._sort_by), reverse=self._sort_reverse)

        start_index = self._top_line
        stop_index = min(len(sessions), self._sessions_number + self._top_line)
        
        for i, session in enumerate(islice(sessions, start_index, stop_index)):
            index = start_index + i + 1
            line_number = i + HEADER_LINES
            session_type = session.type.ljust(4).upper()
            details = ("%s:%d --> %s:%d" % (session.source_ip, session.source_port, session.dest_ip, session.dest_port)).ljust(47)
            rx_rate = get_rate_string(session.rx_bps).ljust(14)
            tx_rate = get_rate_string(session.tx_bps).ljust(14)
            time_string = _get_time_string(session.time)
            display_line = "| %3d | %s | %s | %s | %s | %s" % (index, session_type, details, rx_rate, tx_rate, time_string)
            display_line = display_line.ljust(len(EMPTY_LINE))
            self._pad.addstr(line_number,
                             0,
                             display_line,
                             self._get_session_color(session))

        sessions_printed = stop_index - start_index
        for i in xrange(sessions_printed + HEADER_LINES, self._sessions_number + HEADER_LINES):
            self._pad.addstr(i, 0, EMPTY_LINE)

        self._pad.refresh(0,
                          0,
                          self._ylocation,
                          self._xlocation,
                          self._ylocation + self.get_y_size(),
                          self._xlocation + self.get_x_size())
