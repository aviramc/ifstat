# TODO: Split into files
from collections import namedtuple

Session = namedtuple('Session', ['type', 'source_ip', 'source_port', 'dest_ip', 'dest_port', 'is_dead', 'is_new', 'rx_bps', 'tx_bps', 'time'])

SimpleStatProcessingData = namedtuple('SimpleStatProcessingData', ['name', 'processor', 'field'])

def _rate_per_second(old_stat, new_stat, interval):
    return (new_stat - old_stat) / (1.0 / interval)

def _process_device_data(old_stats, new_stats, interval):
    stat_data = [SimpleStatProcessingData(name='rx_bps', processor=_rate_per_second, field='rx_bytes'),
                 SimpleStatProcessingData(name='tx_bps', processor=_rate_per_second, field='tx_bytes'),
                 SimpleStatProcessingData(name='rx_errors_bps', processor=_rate_per_second, field='rx_errors'),
                 SimpleStatProcessingData(name='tx_errors_bps', processor=_rate_per_second, field='tx_errors'),
                ]

    stats = {}

    for data in stat_data:
        stats[data.name] = data.processor(old_stats[data.field], new_stats[data.field], interval)

    return stats

def _process_session_data(old_stats, new_stats, interval):
    sessions = []
    for session_key, raw_session_data in new_stats.iteritems():
        session_type, source_ip, source_port, dest_ip, dest_port = session_key
        is_new = session_key not in old_stats
        sessions.append(Session(type=session_type,
                                source_ip=source_ip,
                                source_port=source_port,
                                dest_ip=dest_ip,
                                dest_port=dest_port,
                                is_dead=raw_session_data.closed,
                                is_new=is_new,
                                rx_bps=(0 if is_new else _rate_per_second(old_stats[session_key].rx_bytes, raw_session_data.rx_bytes, interval)),
                                tx_bps=(0 if is_new else _rate_per_second(old_stats[session_key].tx_bytes, raw_session_data.tx_bytes, interval)),
                                time=raw_session_data.last_packet_time - raw_session_data.start_time))

    # XXX: Add sessions that don't exist anymore as dead
    for session_key, raw_session_data in old_stats.iteritems():
        session_type, source_ip, source_port, dest_ip, dest_port = session_key
        if session_key not in new_stats:
            sessions.append(Session(type=session_type,
                                    source_ip=source_ip,
                                    source_port=source_port,
                                    dest_ip=dest_ip,
                                    dest_port=dest_port,
                                    is_dead=True,
                                    is_new=False,
                                    rx_bps=0,
                                    tx_bps=0,
                                    time=raw_session_data.last_packet_time - raw_session_data.start_time))
        
    return sessions

DataProcessors = {'device': _process_device_data,
                  'sessions': _process_session_data,
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
