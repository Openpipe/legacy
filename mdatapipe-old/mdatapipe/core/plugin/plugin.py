"""
    A mdatapipe plugin is a regular python module which provides
    a class named "Plugin" derived from the class "PipelinePlugin".

    The load_module() function imports the python module and invokes the
    Plugin's class __init__() method.

    The "PipelinePlugin" base class provides all the methods that a plugin
    can use to interace with the the pipeline, this is in fact the plugin API.

    The following callbacks are available:
        - on_load(self):
        invoked when the plugin is loaded

        - on_input(self, value):
        invoked when a item is received

        - on_buffer_full(self, buffer):
        invoked when the config contains "buffer_size" and the buffer is full

        - on_stop(self)
        invoked when the plugin is stopped

    The following methods are available:
        - put(item):
        write an item into the input queue of an instance of the next plugin
        - put_all(value)
        put a value into the input queues of all the instances of the next plugin
"""
import sys
import sqlite3
import logging
from logging.handlers import WatchedFileHandler
from time import time, process_time
from os import makedirs, environ
from os.path import join, exists, expanduser, dirname
from mdatapipe.client.colorhelper import info
from mdatapipe.core.plugin.base import PipelineBasePlugin
from datetime import datetime


class UnsupportedTypeError(Exception):
    """Raise when the plugin receives an item of an unsupported type"""


class PipelinePlugin(PipelineBasePlugin):

    def __init__(self, config=None, name=None):
        """ Called immeditaly after the plugin is imported """
        super(PipelinePlugin, self).__init__(config, name)
        self.buffer_size = 1
        self.buffer = []
        self._stop_on_error = False
        self.start_time = None             # Time at which the plugin was started
        self.execution_time = 0         # Time spent on callback execution

        if hasattr(self, 'config') and isinstance(self.config, dict) and 'buffer_size' in self.config:
            self.buffer_size = self.config['buffer_size']
        if hasattr(self, 'on_input'):
            self.run = self.input_loop
        elif hasattr(self, 'on_input_buffer'):
            self.run = self.input_buffer_loop
        else:
            self.control_sender.send(None)  # terminate pipeline:
            raise Exception("Plugin misses an on_input() randon_input_buffer()!\n"+self.name)

        if hasattr(self, 'SQLITE_DB_SQL'):
            self._init_db()
        else:
            self.cursor = None

        if hasattr(self, 'on_load'):
            self.on_load()

    def _on_first(self, item):
        supported_types = getattr(self, 'supported_types', [])
        if supported_types:
            is_valid = False
            for input_type in supported_types:
                if isinstance(item, input_type):
                    is_valid = True
                    break
            if not is_valid:
                supported_types = str(list([x.__name__ for x in supported_types]))
                msg = "Got unsupported item of type '%s', expected %s " % (type(item).__name__, supported_types)
                self.control_sender.send(None)  # terminate pipeline
                raise UnsupportedTypeError(msg)

        if hasattr(self, 'on_first'):
            self.on_first(item)

    def _init_db(self):
        sqite_db_sql = self.SQLITE_DB_SQL
        filename = self.name.replace(".py", ".db")
        filename = filename.replace("/", "_")
        db_filename = join(expanduser("~"), ".datapipe", filename)
        if not exists(dirname(db_filename)):
            makedirs(dirname(db_filename))
        self.conn = conn = sqlite3.connect(db_filename)
        self.cursor = conn.cursor()
        self.cursor.execute(sqite_db_sql)

    def _setup_logging(self):
        handlers = []

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logging.Formatter('%(asctime)-15s {0} %(message)s'.format(self.name)))
        handlers.append(consoleHandler)
        loglevel = environ.get('LOG_LEVEL', 'INFO')
        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)

        consoleHandler.setLevel(numeric_level)

        if self.log_dir:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            fileName = join(self.log_dir, self.name)+".log"
            fileHandler = WatchedFileHandler(fileName, mode='w')
            fileHandler.setLevel(logging.DEBUG)
            fileHandler.setFormatter(formatter)
            handlers.append(fileHandler)
            numeric_level = logging.DEBUG

        logging.basicConfig(handlers=handlers, level=numeric_level)

    def _on_loop_start(self):
        self._setup_logging()
        self.start_cpu_time = process_time()
        self.is_transport = self.name.startswith("transport") or self.name.startswith("test")
        self.loop_count = 0
        self.start_time = None
        self._on_start()
        logging.debug("Starting input loop")

    def _on_loop_exit(self):
        if hasattr(self, 'on_exit'):
            logging.debug("Calling on_exit()")
            self.on_exit()
        # Close all descendents
        self._close_descendents()
        self._on_exit()
        logging.shutdown()

    def _execution_error(self, item):
        msg = (
            "---------- Plugin %s execution failed, for source item (%d) ----------:"
            % (self.name, self.get_item_count))
        logging.exception(str(item) + "\n" + msg)
        if self._stop_on_error:
            self.control_sender.send(None)  # terminate pipeline

    def input_loop(self):  # NOQA: C901
        self._on_loop_start()

        while True:
            reply = None
            item = self.get()

            if item is None:
                logging.debug("END on empty input list")
                break

            if self.is_transport and len(self.out_pipe_list) > 0:
                self.put(item)

            if self.loop_count == 0:
                try:
                    self._on_first(item)
                except UnsupportedTypeError:
                    logging.exception(item)

            self.loop_count += 1
            execution_start_time = time()
            try:
                reply = self.on_input(item)
            except:  # NOQA: E722
                self._execution_error(item)
                current_time = time()
                self.elapsed_time = current_time - self.start_time
            if reply is not None:
                self.current_in_conn.send(reply)
            self.execution_time += time() - execution_start_time

        self._on_loop_exit()

    def input_buffer_loop(self):
        self._on_loop_start()

        while True:
            # We cannot close descendents because we have data to flush
            item = self.get()
            if item is None:
                logging.debug("END on empty input list")
                break
            if self.loop_count == 0:
                try:
                    self._on_first(item)
                except UnsupportedTypeError:
                    logging.exception(item)
                    self.control_sender.send(None)  # terminate pipeline
                    raise
            self.loop_count += 1
            self.buffer.append(item)
            if len(self.buffer) == self.buffer_size:
                self._flush_input_buffer()

        # Flush remaining entries
        self._flush_input_buffer()

        self._on_loop_exit()

    def _flush_input_buffer(self):
        execution_start_time = time()
        try:
            self.on_input_buffer(self.buffer)
        except:  # NOQA: E722
            self._execution_error(None)
        finally:
            self.buffer = []
            current_time = time()
            self.execution_time += current_time - execution_start_time
            self.execution_time += time() - execution_start_time

    def _on_start(self):

        stdout = self._config.get("stdout")
        if stdout:
            sl = StreamToLogger(sys.stdout, stdout)
            sys.stdout = sl

        stderr = self._config.get("stderr")
        if stderr:
            sl = StreamToLogger(sys.stderr, stderr)
            sys.stderr = sl

        if hasattr(self, 'on_start'):
            self.on_start()

    def _on_exit(self):

        if self.cursor:
            self.cursor.close()

        total_time = self.execution_time + self.get_time + self.put_time
        if total_time:
            ops = int(self.put_item_count / total_time)
            ops = '{:,}'.format(ops)
        else:
            ops = None

        if total_time:
            exec_perc = str(float(("%0.2f" % (self.execution_time / total_time * 100))))+"%"
            get_wait = str(float(("%0.2f" % (self.get_time / total_time * 100))))+"%"
            put_wait = str(float(("%0.2f" % (self.put_time / total_time * 100))))+"%"
        else:
            exec_perc = 0
            get_wait = 0
            put_wait = 0

        total_time = float(("%0.2f" % total_time))
        put_item_count = '{:,}'.format(self.put_item_count)
        get_item_count = '{:,}'.format(self.get_item_count)
        detail = "In {}; Out {}; ".format(info(get_item_count), info(put_item_count))
        detail += "{} O/s; T: {}s".format(info(ops), info(total_time))
        detail += "; E: {}".format(info(exec_perc))
        detail += " I: {}".format(info(get_wait))
        detail += " O: {}".format(info(put_wait))
        cpu_time = process_time() - self.start_cpu_time
        detail += " CPU Time {}s".format(info(ops), info(cpu_time))
        self.report('{:>50} Done, {}'.format(info(self.desc), detail))


class StreamToLogger(object):
    _orig_stdout = sys.stdout

    def __init__(self, original_log, filename):
        self._orig = original_log
        self._file = open(filename, 'a')

    def write(self, data):
        if len(data) > 10:
            self._file.write(str(datetime.now()) + " " + data+"\n")

    def flush(self):
        self._orig.flush()
