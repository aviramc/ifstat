from collections import namedtuple

SimpleStatProcessingData = namedtuple('SimpleStatProcessingData', ['name', 'processor', 'field'])

# TODO: Duplicate code
def _rate_per_second(old_stat, new_stat, interval):
    return (new_stat - old_stat) / (1.0 / interval)

def process(old_stats, new_stats, interval):
    stat_data = [SimpleStatProcessingData(name='rx_bps', processor=_rate_per_second, field='rx_bytes'),
                 SimpleStatProcessingData(name='tx_bps', processor=_rate_per_second, field='tx_bytes'),
                 SimpleStatProcessingData(name='rx_errors_bps', processor=_rate_per_second, field='rx_errors'),
                 SimpleStatProcessingData(name='tx_errors_bps', processor=_rate_per_second, field='tx_errors'),
                ]

    stats = {}

    for data in stat_data:
        stats[data.name] = data.processor(old_stats[data.field], new_stats[data.field], interval)

    return stats
