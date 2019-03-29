from datetime import timedelta
from itertools import chain
from collections import deque
from sys import getsizeof, stderr


def time_format(time_in_seconds, precise=True):
    delta = timedelta(seconds=time_in_seconds)

    deltaMinutes = delta.seconds // 60
    deltaHours = delta.seconds // 3600
    deltaMinutes -= deltaHours * 60
    deltaWeeks = delta.days // 7
    deltaSeconds = delta.seconds - deltaMinutes * 60 - deltaHours * 3600
    deltaDays = delta.days - deltaWeeks * 7
    deltaMilliSeconds = delta.microseconds // 1000
    deltaMicroSeconds = delta.microseconds - deltaMilliSeconds * 1000

    valuesAndNames = [
            (deltaWeeks, "week"),
            (deltaDays, "day"),
            (deltaHours, "hour"),
            (deltaMinutes, "m"),
            (deltaSeconds, "s")
    ]
    if precise:
        valuesAndNames.append((deltaMilliSeconds, "ms"))
        valuesAndNames.append((deltaMicroSeconds, "μs"))

    text = ""
    for value, name in valuesAndNames:
        if value > 0:
            text += len(text) and ":" or ""
            text += "%d%s" % (value, name)
    return text


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


def total_size(o, handlers={}, verbose=False):
    """ Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    dict_handler = lambda d: chain.from_iterable(d.items())  # NOQA: E731
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                    }
    all_handlers.update(handlers)     # user handlers take precedence
    seen = set()                      # track which object id's have already been seen
    default_size = getsizeof(0)       # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)
