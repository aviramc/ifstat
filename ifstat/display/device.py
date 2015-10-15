import curses

from .rate import get_rate_string

FOOTER_LINE = "+--------------------------------------------------------------------------------------------------------------------"
PAD_X_SIZE = len(FOOTER_LINE) + 1

class DevicePad(object):
    def __init__(self, device_name, speed_graph_height=10, ylocation=0, xlocation=0, colors=None):
        self._device_name = device_name
        self._speed_graph_height = speed_graph_height
        self._ylocation = ylocation
        self._xlocation = xlocation
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

    def get_x_size(self):
        return PAD_X_SIZE + 1

    def get_y_size(self):
        # Height is calculated as follows:
        #   Speed graph height (configurable)
        # + Line for the rate of the graph
        # + Stats display lines
        return self._speed_graph_height + 1 + len(self._stats_display_functions)

    def key(self, key):
        pass

    def _display_device_stats(self, start_line, stats):
        for current_line, display_function in enumerate(self._stats_display_functions, start=start_line):
            display_function(current_line, stats)

    def _display_footer_line(self, line, stats):
        self._pad.addstr(line, 0, FOOTER_LINE)

    def _display_device_line(self, line, stats):
        self._pad.addstr(line, 0, "| Device: %s" % (self._device_name,))

    def _display_empty_line(self, line, stats):
        self._pad.addstr(line, 0, "|")

    def _display_rx_stats_line(self, line, stats):
        self._pad.addstr(line, 0, "| RX Rate: %s Bps  RX Error rate: %d Eps" % (get_rate_string(stats['rx_bps']),
                                                                                stats['rx_errors_bps']))

    def _display_tx_stats_line(self, line, stats):
        self._pad.addstr(line, 0, "| TX Rate: %s Bps  TX Error rate: %d Eps" % (get_rate_string(stats['tx_bps']),
                                                                                stats['tx_errors_bps']))

    def display(self, stats):
        if not stats:
            return
        # TODO: Speed graph.
        self._pad.addstr(0, 0, "| Rate |")
        for current_line in xrange(1, self._speed_graph_height):
            self._pad.addstr(current_line, 0, "|      |")

        self._display_device_stats(current_line, stats)

        self._pad.refresh(0,
                          0,
                          self._ylocation,
                          self._xlocation,
                          self._ylocation + self.get_y_size(),
                          self._xlocation + self.get_x_size())
