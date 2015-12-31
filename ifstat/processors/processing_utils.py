def stat_per_interval(old_stat, new_stat, interval):
    return (new_stat - old_stat) / (1.0 / interval)
