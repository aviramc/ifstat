"""
TCP/UDP Session statistics collector.
This module perform packet sniffing and so requires high privileges
"""

from multiprocessing import Manager, Value, Process
from collections import namedtuple
from copy import deepcopy
import socket
import dpkt
import pcap
import time

# TCP/UDP session descriptor
Session = namedtuple('Session', ['start_time',
                                 'last_packet_time',
                                 'rx_bytes',
                                 'tx_bytes',
                                 'closed',
                                 ])
# TCP/UDP packet data
Packet = namedtuple('Packet', ['type', 'source_ip', 'source_port', 'dest_ip', 'dest_port', 'length', 'last'])

PACKET_TYPES = {dpkt.tcp.TCP: 'tcp',
                dpkt.udp.UDP: 'udp',
               }

def _is_last_packet(parsed_packet, packet_type):
    if packet_type != 'tcp':
        return False
    is_fin = bool(parsed_packet.ip.tcp.flags & dpkt.tcp.TH_FIN)
    is_rst = bool(parsed_packet.ip.tcp.flags & dpkt.tcp.TH_RST)
    return is_fin or is_rst
        
def _parse_packet(packet):
    # XXX: We're assuming that packets are either IP/TCP or IP/UDP over Ethernet
    parsed_packet = dpkt.ethernet.Ethernet(packet)

    if type(parsed_packet.data) != dpkt.ip.IP:
        return

    packet_type = PACKET_TYPES[type(parsed_packet.ip.data)]
    session_packet = getattr(parsed_packet.ip, packet_type)

    return Packet(type=packet_type,
                  source_ip=socket.inet_ntoa(parsed_packet.ip.src),
                  source_port=session_packet.sport,
                  dest_ip=socket.inet_ntoa(parsed_packet.ip.dst),
                  dest_port=session_packet.dport,
                  length=parsed_packet.ip.len,
                  last=_is_last_packet(parsed_packet, packet_type))

def _get_session_key(packet, stats):
    key = (packet.type, packet.dest_ip, packet.dest_port, packet.source_ip, packet.source_port)
    if key in stats:
        return key
    
    key = (packet.type, packet.source_ip, packet.source_port, packet.dest_ip, packet.dest_port)
    return key

def _packet_side(packet_data, packet_key):
    packet_type, source_ip, source_port, dest_ip, dest_port = packet_key
    if packet_data.source_ip == source_ip and packet_data.source_port == source_port:
        return 'tx_side'
    return 'rx_side'

def _get_new_rx_bytes(packet_data, side):
    if side == 'rx_side':
        return packet_data.length
    return 0

def _get_new_tx_bytes(packet_data, side):
    if side == 'tx_side':
        return packet_data.length
    return 0

def _process_packet(packet, stats):
    # TODO: If the packet is TCP, remove after FIN/RST
    packet_data = _parse_packet(packet)
    if packet_data is None:
        return

    key = _get_session_key(packet_data, stats)

    side = _packet_side(packet_data, key)

    closed = packet_data.last
    if key in stats:
        start_time = stats[key].start_time
        rx_bytes = stats[key].rx_bytes + _get_new_rx_bytes(packet_data, side)
        tx_bytes = stats[key].tx_bytes + _get_new_tx_bytes(packet_data, side)
        last_packet_time = time.time()
    else:
        start_time = last_packet_time = time.time()
        rx_bytes = _get_new_rx_bytes(packet_data, side)
        tx_bytes = _get_new_tx_bytes(packet_data, side)

    stats[key] = Session(start_time=start_time,
                         rx_bytes=rx_bytes,
                         tx_bytes=tx_bytes,
                         last_packet_time=last_packet_time,
                         closed=closed)

def _clean_closed_sessions(stats, udp_session_timeout, tcp_session_timeout):
    current_time = time.time()
    # XXX: Not iterating directly over the dictionary as we change it in the loop
    for key in stats.keys():
        session_type, source_ip, source_port, dest_ip, dest_port = key
        session = stats[key]

        session_timeout = udp_session_timeout if session_type == 'udp' else tcp_session_timeout
        if session.closed or current_time - session.last_packet_time > session_timeout:
            stats.pop(key)

def process_sessions(device, stats, running, udp_session_timeout, tcp_session_timeout):
    # TODO: What's the snaplen required to capture everything?
    # TODO: This is very inefficient
    pcap_object = pcap.pcap(device)
    pcap_object.setfilter('tcp or udp')
    for packet in pcap_object:
        if packet is None:
            _clean_closed_sessions(stats, udp_session_timeout, tcp_session_timeout)
            continue
        packet_time, packet_data = packet
        _process_packet(packet_data, stats)
        _clean_closed_sessions(stats, udp_session_timeout, tcp_session_timeout)

        if not running.value:
            break

    pcap_object.close()

class NetworkSessions(Process):
    def __init__(self, device, udp_session_timeout=10, tcp_session_timeout=120):
        self._manager = Manager()
        self._stats = self._manager.dict()
        self._running = Value('b', False)
        self._device = device
        self._udp_session_timeout = udp_session_timeout
        self._tcp_session_timeout = tcp_session_timeout

        super(NetworkSessions, self).__init__()

    def stop(self):
        self._running.value = True

    def get_stats(self):
        return deepcopy(self._stats)

    def run(self):
        self._running.value = True
        process_sessions(self._device,
                         self._stats,
                         self._running,
                         self._udp_session_timeout,
                         self._tcp_session_timeout)
