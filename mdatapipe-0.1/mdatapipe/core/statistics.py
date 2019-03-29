from time import process_time, perf_counter
from ..core.utils import time_format


class StatsRecord(object):

    def __init__(self, label):
        self.label = label
        self.start_process_time = 0
        self.total_process_time = 0
        self.start_perf_counter = 0
        self.total_perf_counter = 0
        self.count = 0

    def start(self):
        self.count += 1
        self.resume()

    def stop(self):
        self.pause()

    def pause(self):
        self.last_process_time = process_time() - self.start_process_time
        self.total_process_time += self.last_process_time
        self.last_perf_counter = perf_counter() - self.start_perf_counter
        self.total_perf_counter += self.last_perf_counter

    def resume(self):
        self.start_process_time = process_time()
        self.start_perf_counter = perf_counter()

    def result(self):
        return {
            'label': self.label,
            'cpu_time': time_format(self.total_process_time),
            'clk_time': time_format(self.total_perf_counter),
            'count': self.count,
        }

    def rollback(self):
        self.count -= 1
        self.total_process_time -= self.last_process_time
        self.total_perf_counter -= self.last_perf_counter
