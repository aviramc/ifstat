from .processors import device, sessions

DataProcessors = {'device': device.process,
                  'sessions': sessions.process,
                 }

class StatProcessor(object):
    def __init__(self, stats):
        self._old_stats = stats

    def process_new_stats(self, new_stats, interval):
        processed_stats = {}
        for stat_type, processor in DataProcessors.iteritems():
            processed_stats[stat_type] = processor(self._old_stats[stat_type],
                                                   new_stats[stat_type],
                                                   interval)
        self._old_stats = new_stats
        return processed_stats
