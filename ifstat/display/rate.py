from itertools import izip

def get_rate_string(rate_bps):
    levels = ['KBps', 'MBps', 'GBps']
    rate_thresholds = [1024, ] * len(levels)

    current_rate_value = rate_bps
    current_rate_name = 'Bps'
    for rate_name, rate_threshold in izip(levels, rate_thresholds):
        if current_rate_value < rate_threshold:
            break
        current_rate_value = current_rate_value / rate_threshold
        current_rate_name = rate_name

    return "%7.2f %4s" % (current_rate_value, current_rate_name)
