"""
Device statistics collectors

This module is for collecting general network device statistics.
Implementation is Linux specific!
"""

from collections import namedtuple
from string import Template

class DeviceCollector(object):
    """
    Collect general Linux based network statistics each interval
    Paramters are the device name (e.g. 'eth0') and interval
    """

    STAT_FILES = {'rx_bytes': ('/sys/class/net/%(device)s/statistics/rx_bytes', int),
                  'tx_bytes': ('/sys/class/net/%(device)s/statistics/tx_bytes', int),
                  'rx_errors': ('/sys/class/net/%(device)s/statistics/rx_errors', int),
                  'tx_errors': ('/sys/class/net/%(device)s/statistics/tx_errors', int),
                 }

    def __init__(self, device):
        self._device = device

    def run(self):
        pass

    def start(self):
        pass

    def join(self):
        pass

    def stop(self):
        pass

    def _get_stat_from_file(self, stat_filename, stat_type):
        with open(stat_filename) as stat_file:
            stat = stat_type(stat_file.read())
        return stat
    
    def get_stats(self):
        stats = {}
        for stat_name, (stat_filename_template, stat_type) in self.STAT_FILES.iteritems():
            stat_filename = stat_filename_template % {'device': self._device}
            stats[stat_name] = self._get_stat_from_file(stat_filename, stat_type)
        return stats
