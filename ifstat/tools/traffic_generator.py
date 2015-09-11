from multiprocessing import Manager, Value, Process
import itertools
import argparse
import signal
import socket
import time
import os
import re

BIND_ADDRESS = '127.0.0.1'
BASE_PORT = 2570

_free_port = BASE_PORT
def _allocate_port():
    global _free_port
    _free_port += 1
    return _free_port
    
class TcpTrafficPair(object):
    def __init__(self, ip, port, send_delay):
        self.ip = ip
        self.port = port
        self._manager = Manager()
        self._running = Value('b', True)
        self.server = Process(target=simple_tcp_server,
                               args=(ip, port, self._running))
        self.client = Process(target=simple_tcp_client,
                               args=(ip, port, send_delay, self._running))

    def start_server(self):
        self.server.start()

    def start_client(self):
        self.client.start()

    def stop(self, wait=True):
        self._running.value = False
        if wait:
            self.server.join()
            self.client.join()

def simple_tcp_server(bind_ip, bind_port, running):
    serv = socket.socket()
    serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv.bind((bind_ip, bind_port))
    serv.listen(1)
    try:
        client, _ = serv.accept()
        try:
            client.setblocking(0)
            while running.value:
                try:
                    receive_buffer = client.recv(1024)
                    if receive_buffer == '':
                        break
                    client.sendall(receive_buffer)
                except socket.error, error_object:
                    if error_object.errno != 11:
                        raise
        finally:
            client.close()
    finally:
        serv.close()

def simple_tcp_client(server_ip, server_port, send_delay, running):
    connection = socket.socket()
    connection.connect((server_ip, server_port))
    try:
        rand_file = open('/dev/urandom')
        while running.value:
            rand_buffer = rand_file.read(1024)
            connection.sendall(rand_buffer)
            receive_buffer = connection.recv(1024)
            time.sleep(send_delay)
    finally:
        connection.close()

def _get_command_indices(pairs, options):
    if not options:
        list_indices = xrange(len(pairs))
    else:
        list_indices = [int(index)
                        for index in options
                        if index.isdigit()]
        range_indices_strings = [range_expression
                                 for range_expression in options
                                 if re.match(r'\d+-\d+', range_expression)]
        range_indices = []
        for range_indice_string in range_indices_strings:
            start, end = (int(i) for i in range_indice_string.split('-'))
            range_indices.extend(range(start, end + 1))
        list_indices.extend(range_indices)
        list_indices = set(list_indices)

        list_indices = [index for index in list_indices
                        if index < len(pairs)]

    return list_indices
        
def _list_command(pairs, options):
    list_indices = _get_command_indices(pairs, options)
    
    print 'Index, Client running?, Server running?, Server IP:PORT'
    for index in list_indices:
        pair = pairs[index]
        print index, pair.client.is_alive(), pair.server.is_alive(), '%s:%d' % (pair.ip, pair.port)

    return True

def _stop_command(pairs, options):
    list_indices = _get_command_indices(pairs, options)

    for index in list_indices:
        print 'Stopping pair', index
        pairs[index].stop(wait=True)
    
    return True

def _start_single(pairs):
    pair = TcpTrafficPair(BIND_ADDRESS, _allocate_port(), 0.5)
    pair.start_server()
    time.sleep(1)
    pair.start_client()
    pairs.append(pair)
    print 'Started a new pair'

def _start_command(pairs, options):
    if not options:
        processes = 1
    else:
        if options[0].isdigit():
            processes = int(options[0])
        else:
            processes = 1

    for i in xrange(processes):
        _start_single(pairs)
    
    return True

def _clean_command(pairs, options):
    pairs_to_remove = [pair for pair in pairs
                       if not pair.server.is_alive() and not pair.client.is_alive()]
    for pair in pairs_to_remove:
        pairs.remove(pair)
    return True

def start(processes):
    pairs = []

    for i in xrange(processes):
        pairs.append(TcpTrafficPair(BIND_ADDRESS, _allocate_port(), 0.5))

    for pair in pairs:
        pair.start_server()
    time.sleep(1)
    for pair in pairs:
        pair.start_client()

    commands = {'quit': lambda *args: False,
                'q': lambda *args: False,
                'list': _list_command,
                'stop': _stop_command,
                'start': _start_command,
                'clean': _clean_command,
               }

    running = True
    while running:
        try:
            user_input = raw_input('--> ').strip().split()
        except EOFError:
            user_input = ['q']
        if user_input:
            command = user_input[0]
            if command in commands:
                command_args = user_input[1:]
                running = commands[command](pairs, command_args)
            else:
                print 'no such command \'%s\'' % (command, )

    print 'Closing all processes...'
    for pair in pairs:
        pair.stop(wait=True)

if '__main__' == __name__:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--connections', '-c', dest='connections', default=0, type=int, help='Number of connections to start immediately')
    args = arg_parser.parse_args()
    start(args.connections)
