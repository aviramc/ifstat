import argparse
import time

from .stat_processor import StatProcessor
from . import getstats

#~~~
from pprint import pprint
#~~~

def main():
    arg_parser = argparse.ArgumentParser(description="ifstat - network interface statistics utility")
    arg_parser.add_argument(dest='device', help='The device name to get stats for')
    arg_parser.add_argument('--interval', '-i', dest='interval', default=1.0, type=float, help='Interval to gather and display stats')

    args = arg_parser.parse_args()

    # TODO: Verify the device exists

    collector = getstats.StatCollector(args.device)
    current_stats = collector.get_stats()
    stat_processor = StatProcessor(current_stats)

    while True:
        time.sleep(args.interval)
        current_stats = collector.get_stats()
        pprint(stat_processor.process_new_stats(current_stats, args.interval))
