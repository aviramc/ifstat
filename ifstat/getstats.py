from .collectors import device

COLLECTORS = {'device': device.DeviceCollector,
             }

class StatCollector(object):
    def __init__(self, device, collectors=None):
        if collectors is None:
            collectors = COLLECTORS.keys()

        self._collectors = {}
        for collector in collectors:
            self._collectors[collector] = COLLECTORS[collector](device)

    def start(self):
        for collector in self._collectors.itervalues():
            collector.start()

    def join(self):
        for collector in self._collectors.itervalues():
            collector.join()

    def get_stats(self):
        stats = {}
        for collector_name, collector_object in self._collectors.iteritems():
            collector_stats = collector_object.get_stats()
            stats[collector_name] = collector_stats
        return stats
