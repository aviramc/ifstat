from collections import namedtuple

StatData = namedtuple('StatData', ['name', 'processor', 'field'])

def rate_per_second(old_stat, new_stat, interval):
    return (new_stat - old_stat) / (1.0 / interval)

def count_per_second(old_stat, new_stat, interval):
    pass

DeviceStatData = [StatData(name='rx_bps', processor=rate_per_second, field='rx_bytes'),
                  StatData(name='tx_bps', processor=rate_per_second, field='tx_bytes'),
                  StatData(name='rx_errors_bps', processor=rate_per_second, field='rx_errors'),
                  StatData(name='tx_errors_bps', processor=rate_per_second, field='tx_errors'),
                 ]
                  
def process_stats(stat_data, old_stats, new_stats, interval):
    stats = {}

    for data in stat_data:
        stats[data.name] = data.processor(old_stats[data.field], new_stats[data.field], interval)

    return stats

class StatProcessor(object):
    def __init__(self, stats):
        self._raw_stats = stats

    def process_new_stats(self, new_stats, interval):
        processed_stats = {}
        if 'device' in new_stats:
            processed_stats['device'] = process_stats(DeviceStatData,
                                                      self._raw_stats['device'],
                                                      new_stats['device'],
                                                      interval)

        self._raw_stats = new_stats
        return processed_stats
