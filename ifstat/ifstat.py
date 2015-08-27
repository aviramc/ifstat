import argparse
import locale
import curses

from .stat_processor import StatProcessor
from .display.sessions import SessionsPad
from . import getstats

DEFAULT_INTERVAL = 10

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
    curses.halfdelay(DEFAULT_INTERVAL)
    try:
        running = True
        while running:
            raw_stats = collector.get_stats()
            current_stats = stat_processor.process_new_stats(raw_stats, args.interval)

            sessions_pad.display(current_stats["sessions"])
            key = window.getch()

            if key == ord('q'):
                collector.stop()
                collector.join()
                running = False
    finally:
        curses.nocbreak()
        curses.echo()
        curses.endwin()
