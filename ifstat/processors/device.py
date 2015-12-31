from collections import namedtuple

from .processing_utils import stat_per_interval

SimpleStatProcessingData = namedtuple('SimpleStatProcessingData', ['name', 'processor', 'field'])

def process(old_stats, new_stats, interval):
    stat_data = [SimpleStatProcessingData(name='rx_bps', processor=stat_per_interval, field='rx_bytes'),
                 SimpleStatProcessingData(name='tx_bps', processor=stat_per_interval, field='tx_bytes'),
                 SimpleStatProcessingData(name='rx_errors_bps', processor=stat_per_interval, field='rx_errors'),
                 SimpleStatProcessingData(name='tx_errors_bps', processor=stat_per_interval, field='tx_errors'),
                ]

    stats = {}

    for data in stat_data:
        stats[data.name] = data.processor(old_stats[data.field], new_stats[data.field], interval)

    return stats
