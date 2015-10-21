from collections import deque
import curses

from .pad_display_manager import PadDisplayManager
from .rate import get_rate_string

FOOTER_LINE = "+--------------------------------------------------------------------------------------------------------------------"
PAD_X_SIZE = len(FOOTER_LINE) + 1
RATE_GRAPH_HEADER_SIZE = 1
RATE_COLUMN_WIDTH = len("| 1024.10 KBps |")

FULL_BAR_SYMBOL = u'\u2588'.encode('UTF-8')
HALF_BAR_SYMBOL = u'\u2584'.encode('UTF-8')

class DevicePad(object):
    def __init__(self, device_name, refresh_interval, rate_graph_height=10, ylocation=0, xlocation=0, colors=None):
        self._device_name = device_name
        self._refresh_interval = refresh_interval
        self._rate_graph_height = rate_graph_height
        self._colors = colors

        self._stats_display_functions = [self._display_footer_line,
                                         self._display_device_line,
                                         self._display_empty_line,
                                         self._display_rx_stats_line,
                                         self._display_tx_stats_line,
                                         self._display_empty_line,
                                         self._display_footer_line,
                                        ]

        self._pad = curses.newpad(self.get_y_size(), self.get_x_size())
        self._pad_display_manager = PadDisplayManager(ylocation, xlocation)

        history_length = ((self.get_x_size() - 4)/ 2 - RATE_COLUMN_WIDTH)
        self._rx_rate_history = deque((0, ) * history_length, maxlen=history_length)
        self._tx_rate_history = deque((0, ) * history_length, maxlen=history_length)

    def get_x_size(self):
        return PAD_X_SIZE + 1

    def get_y_size(self):
        # Height is calculated as follows:
        #   Speed graph height (configurable)
        # + Line for the rate of the graph
        # + Stats display lines
        return self._rate_graph_height + 1 + len(self._stats_display_functions)

    def key(self, key):
        self._pad_display_manager.key(key)

    def _display_device_stats(self, start_line, stats):
        for current_line, display_function in enumerate(self._stats_display_functions, start=start_line):
            display_function(current_line, stats)

    def _display_footer_line(self, line, stats):
        self._pad.addstr(line, 0, FOOTER_LINE)

    def _display_device_line(self, line, stats):
        self._pad.addstr(line, 0, "| Device: %s          Refresh every %.2f seconds" % (self._device_name, self._refresh_interval))

    def _display_empty_line(self, line, stats):
        self._pad.addstr(line, 0, "|")

    def _display_rx_stats_line(self, line, stats):
        self._pad.addstr(line, 0, "| RX Rate: %s      RX Error rate: %d Eps" % (get_rate_string(stats['rx_bps']),
                                                                                stats['rx_errors_bps']))

    def _display_tx_stats_line(self, line, stats):
        self._pad.addstr(line, 0, "| TX Rate: %s      TX Error rate: %d Eps" % (get_rate_string(stats['tx_bps']),
                                                                                stats['tx_errors_bps']))

    def display(self, maxy, maxx, stats):
        if not stats:
            return

        self._rx_rate_history.append(stats['rx_bps'])
        self._tx_rate_history.append(stats['tx_bps'])
        
        display_rate_graph(self._rx_rate_history,
                           self._pad,
                           0,
                           0,
                           self._rate_graph_height,
                           self.get_x_size() / 2,
                           rate_string='RX Rate',
                           colors=self._colors,
                           column_color='green')
        
        display_rate_graph(self._tx_rate_history,
                           self._pad,
                           0,
                           self.get_x_size() / 2,
                           self._rate_graph_height,
                           self.get_x_size() / 2,
                           rate_string='TX Rate',
                           colors=self._colors,
                           column_color='red')

        self._display_device_stats(self._rate_graph_height + RATE_GRAPH_HEADER_SIZE, stats)

        self._pad_display_manager.refresh(self._pad,
                                          maxy,
                                          maxx,
                                          self.get_y_size(),
                                          self.get_x_size())

def _get_rate_string_for_line(current_height, total_height, max_rate):
    height_ratio = float(current_height) / total_height
    return "| %s |" % (get_rate_string(height_ratio * max_rate),)

def _get_graph_symbol(current_height, total_height, rate, max_rate):
    symbol_range = max_rate / total_height
    min_rate_for_non_empty = (float(current_height) / total_height * max_rate) - symbol_range
    min_rate_for_full = min_rate_for_non_empty + (symbol_range / 2.)
    if rate > min_rate_for_non_empty:
        if rate >= min_rate_for_full:
            return FULL_BAR_SYMBOL
        return HALF_BAR_SYMBOL
    return ' '

def _get_graph_string_for_line(current_height, total_height, max_value, history):
    if max_value == 0:
        return ''

    height_ratio = float(current_height) / total_height
    current_position = 0
    line_symbols = []
    for rate in history:
        # line_symbols.append(_get_graph_symbol(height_ratio, rate, max_value))
        line_symbols.append(_get_graph_symbol(current_height, total_height, rate, max_value))
    return ''.join(line_symbols)

def display_rate_graph(rate_history, pad, ylocation, xlocation, ysize, xsize, rate_string='Rate', colors=None, column_color=None):
    pad.addstr(ylocation, xlocation, "| %s |" % (rate_string.ljust(RATE_COLUMN_WIDTH - 4),))
    start_line = ylocation + 1
    max_rate = max(rate_history)
    for line, current_height in enumerate(xrange(ysize, 0, -1), start=start_line):
        rate_string = _get_rate_string_for_line(current_height, ysize, max_rate)
        pad.addstr(line, xlocation, rate_string)
        pad.addstr(line,
                   xlocation + RATE_COLUMN_WIDTH,
                   _get_graph_string_for_line(current_height,
                                              ysize,
                                              max_rate,
                                              rate_history),
                    curses.color_pair(colors[column_color]))

    return line
