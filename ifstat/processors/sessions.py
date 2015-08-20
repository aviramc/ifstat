from collections import namedtuple

Session = namedtuple('Session', ['type', 'source_ip', 'source_port', 'dest_ip', 'dest_port', 'is_dead', 'is_new', 'rx_bps', 'tx_bps', 'time'])

def _rate_per_second(old_stat, new_stat, interval):
    return (new_stat - old_stat) / (1.0 / interval)

def process(old_stats, new_stats, interval):
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
