import logging
import os
import sqlite3
from enum import IntEnum
from logging.handlers import WatchedFileHandler
from os.path import join
from os import environ
from mdatapipe.core.dynaconf import DynamicConfig
from itertools import cycle
from collections import defaultdict
from os.path import expanduser, exists, dirname
from os import makedirs


class PipelinePluginBase():

    class ConnType(IntEnum):
        INPUT = 0
        OUTPUT = 1
        EVENTS = 2
        CONTROL = 3
        EXTRA_OUTPUT = 4

    class Health(IntEnum):
        OK = 0
        FAILED = 1

    class State(IntEnum):
        LOADING = 0
        LOADED = 1
        STARTING = 2
        STARTED = 3
        CONTROL = 4  # Waiting for control
        RECEIVE = 5
        EXECUTE = 6
        SEND = 7
        TERMINATING = 8
        TERMINATED = 9

    def __init__(self, instance_id, config=None):

        if config is None:
            config = {}
        self.instance_id = instance_id

        # Set empty connection lists for every type
        self.conn_list = {}
        for conn_type in self.ConnType:
            self.conn_list[conn_type] = defaultdict(dict)

        # List of connections to be checked during loop
        self.connection_check_list = None

        # Used for round-robin around all available ouput connections
        self.current_output_list = []
        self.current_output_list_iter = []

        self.get_item_count = 0
        self.state = None
        self._setup_logging()
        self.init(instance_id)
        self.config = config
        self._dynaconf = DynamicConfig(config)
        self.is_transport = instance_id.startswith("transport") or instance_id.startswith("test")

    def _init_db(self):
        sqite_db_sql = self.SQLITE_DB_SQL
        filename = self.name
        filename = '_'.join(filename.split("_")[:-2])
        db_filename = join(expanduser("~"), ".mdatapipe", filename+".db")
        if not exists(dirname(db_filename)):
            makedirs(dirname(db_filename))
        self.conn = conn = sqlite3.connect(db_filename)
        self.cursor = conn.cursor()
        self.cursor.execute(sqite_db_sql)

    def start(self):
        self.state = self.State.STARTING
        if hasattr(self, 'SQLITE_DB_SQL'):
            self._init_db()
        else:
            self.cursor = None
        if hasattr(self, "on_start"):
            self.logger.debug("Calling on_start()")
            self.on_start()
        self.state = self.State.STARTED

    def load(self):
        event_handler, control_manager = None, None
        self.state = self.State.LOADING
        return event_handler, control_manager

    def setup(self):
        self.state = self.State.STARTING
        if hasattr(self, "on_setup"):
            self.logger.debug("Calling on_setup()")
            self.on_setup()
        self.state = self.State.STARTED

    def exit(self):
        if hasattr(self, "on_exit"):
            self.logger.debug("Calling on_exit()")
            self.on_exit()

    def _setup_logging(self):
        loglevel = environ.get('LOG_LEVEL', 'INFO')
        logdir = environ.get('LOG_DIR')
        numeric_level = getattr(logging, loglevel.upper(), None)

        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        name = getattr(self, "instance_id", type(self).__name__)
        self.logger = logging.getLogger(name)

        if logdir:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            fileName = join(logdir, name)+".log"
            fileHandler = WatchedFileHandler(fileName, mode='w')
            fileHandler.setFormatter(formatter)
            self.logger.addHandler(fileHandler)
            numeric_level = logging.DEBUG
        else:
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logging.Formatter('%(asctime)-15s {0} %(message)s'.format(name)))
            self.logger.addHandler(consoleHandler)

        self.logger.setLevel(numeric_level)

    def _add_connection(self, conn_type, connection, label=None):
        self.logger.debug(
            '_add_connection %d %s %s %s', os.getpid(), connection, conn_type, label
        )
        self.conn_list[conn_type][label] = connection
        self.connection_check_list = self.controls + self.inputs

    def add_input_connection(self, conn, label=None):
        self._add_connection(self.ConnType.INPUT, conn, label)

    def add_output_connection(self, conn, label=None):
        self._add_connection(self.ConnType.OUTPUT, conn, label)
        self.current_output_list.append((label, conn))
        self.current_output_list_cycle = cycle(self.current_output_list)

    def add_extra_output_connection(self, extra_label, conn, label=None):
        self.logger.debug(
            'add_extra_output_connection %s %s', extra_label, label
        )
        self.conn_list[self.ConnType.EXTRA_OUTPUT][extra_label][conn] = label

    def add_control_connection(self, conn, label=None):
        self._add_connection(self.ConnType.CONTROL, conn, label)

    def add_events_connection(self, conn, label=None):
        self._add_connection(self.ConnType.EVENTS, conn, label)

    def del_input_connection(self, connection):
        if len(self.conn_list[self.ConnType.INPUT]) == 0:  # Got "ITEM", "None" on control connection
            return
        label_to_delete = False
        for label, value in self.conn_list[self.ConnType.INPUT].items():
            if value == connection:
                label_to_delete = label
                break

        self.logger.debug(
            '_del_input_connection %d %s %s', os.getpid(), connection, label_to_delete
        )

        del self.conn_list[self.ConnType.INPUT][label_to_delete]
        self.connection_check_list = self.controls + self.inputs

    @property
    def controls(self):
        control_list = []
        for label, connection in self.conn_list[self.ConnType.CONTROL].items():
            control_list.append(connection)
        return control_list

    @property
    def inputs(self):
        input_list = []
        for label, connection in self.conn_list[self.ConnType.INPUT].items():
            input_list.append(connection)
        return input_list

    def get_all_connections(self, conn_type):
        for label, connection in self.conn_list[conn_type].items():
            yield label, connection
