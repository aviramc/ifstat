import argparse
import locale
import curses
import time

from .stat_processor import StatProcessor
from .display.sessions import SessionsPad
from . import getstats

def main():
    arg_parser = argparse.ArgumentParser(description="ifstat - network interface statistics utility")
    arg_parser.add_argument(dest='device', help='The device name to get stats for')
    arg_parser.add_argument('--interval', '-i', dest='interval', default=1.0, type=float, help='Interval to gather and display stats')

    args = arg_parser.parse_args()

    # TODO: Verify the device exists

    collector = getstats.StatCollector(args.device)
    collector.start()
    raw_stats = collector.get_stats()
    stat_processor = StatProcessor(raw_stats)

    window = curses.initscr()
    sessions_pad = SessionsPad()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    # XXX: halfdelay is in tenths of seconds
    curses.halfdelay(int(args.interval * 10))
    last_time = time.time()
    current_stats = {"device": {}, "sessions": []}
    try:
        running = True
        while running:
            # XXX: Get & process new stats only when the intervals have passed
            current_time = time.time()
            if current_time - last_time >= args.interval:
                raw_stats = collector.get_stats()
                current_stats = stat_processor.process_new_stats(raw_stats, args.interval)
                last_time = current_time

            sessions_pad.display(current_stats["sessions"])
            key = window.getch()

            if key == ord('q'):
                collector.stop()
                running = False

    finally:
        curses.nocbreak()
        curses.echo()
        curses.endwin()
