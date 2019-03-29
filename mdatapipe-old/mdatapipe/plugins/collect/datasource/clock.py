from time import time, sleep
from mdatapipe.core.plugin import PipelinePlugin

"""
Description: Produces the current time (timestamp) at regular intervals
"""


class Plugin(PipelinePlugin):

    def on_input(self, item):
        start_time = item

        interval = self.config.get('interval', "0")
        interval = time2seconds(interval)
        count = self.config.get('max_count', 0)
        repeat_forever = (count == 0)

        self.put_all(start_time)
        if not repeat_forever:
            count -= 1
        while repeat_forever or count > 0:
            if interval:
                sleep(interval)
            self.put_all(time())
            if not repeat_forever:
                count -= 1


def time2seconds(value):
    SECONDS_MAP = {'s': 1, 'm': 60, 'h': 60*60, 'd': 24 * 60 * 60}
    number = ''
    unit = 's'
    if isinstance(value, int):
        return value
    for char in value:
        if char.isdigit():
            number += char
        else:
            unit = char
            break
    multiplier = SECONDS_MAP[unit]
    return int(number) * multiplier
