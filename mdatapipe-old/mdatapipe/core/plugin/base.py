import logging
from multiprocessing import Process
from time import time
from os import environ
from mdatapipe.core.plugin.dynaconf import DynamicConfig
from mdatapipe.core.plugin.timeout import timeout
from multiprocessing.connection import wait


class PipelineBasePlugin(Process):

    def __init__(self, config=None, name=None):

        """ Called immeditaly after the plugin is imported """
        if name is None:
            name = self.__class__.__name__
        super(PipelineBasePlugin, self).__init__(name=name)

        self.in_pipe_list = []          # List of input pipes
        self.out_pipe_list = []         # List of output pipes
        self._config = {}               # Internal module config, can only be set by pipeline

        self.current_out_index = 0      # Index for the current output pipe
        self.put_item_count = 0
        self.get_time = 0
        self.put_time = 0
        self.get_item_count = 0
        self._config_watch = {}         # List of dynamic config mappings
        self.current_in_conn = None     # Last connection used to get data

        self.log_dir = environ.get('LOG_DIR')

        all_config = getattr(self, 'config', {})

        if config and isinstance(all_config, dict):
            # Merge default config with supplied config
            if all_config != {}:
                all_config.update(config)
            else:
                all_config = config
        self._dynaconf = DynamicConfig(all_config)
        self.config = all_config    # Config may be used during the load phase
        self.name = self.desc = name
        self._is_null_output = False

    def get(self, close_all_descendents=True):
        """
            Get one element from the input pipes, using round-robin
            If all pipes are closed, raise an EOFError
        """
        start_time = time()
        get_item = None
        get_conn = len(self.in_pipe_list) > 0   # Only get if there are connections available
        while get_conn:
            in_conn_list = [x[0] for x in self.in_pipe_list]
            available_objects = wait(in_conn_list)
            available_connection = available_objects[0]
            label = [x[1] for x in self.in_pipe_list if x[0] == available_connection][0]
            logging.debug("GET FROM %s", label)
            item = available_connection.recv()
            logging.debug("GOT %s", str(item))

            if item is None:
                # Delete current connection from list
                new_in_pipe_list = [x for x in self.in_pipe_list if x[0] != available_connection]
                self.in_pipe_list = new_in_pipe_list
                get_conn = len(self.in_pipe_list) > 0
            else:
                get_item = item
                get_conn = False

        if item:
            self.get_item_count += 1
            self.config = self._dynaconf.render(item)
            self.refresh_status()
        self.get_time += time() - start_time

        return get_item

    @timeout(5)
    def timed_send(self, item):
        conn, label = self.out_pipe_list[self.current_out_index]
        logging.debug("SEND TO %s: %s", label, str(item))
        conn.send(item)

    def put(self, item, wait_for_reply=False):
        if self._is_null_output:
            return

        # Fail if a erroneous plugin tries to send a None value
        assert(item is not None)

        start_time = time()
        if len(self.out_pipe_list) == 0:
            raise Exception("Put() called  without an output pipe")
        self.timed_send(item)
        self.put_item_count += 1
        if wait_for_reply:
            reply = self.out_pipe_list[self.current_out_index].recv()
            return reply
        self.current_out_index += 1
        if self.current_out_index >= len(self.out_pipe_list):
            self.current_out_index = 0
        self.last_time = time()
        self.put_time += time() - start_time

    def set_null_output(self, value):
        self._is_null_output = value

    def put_all(self, item):
        """ Put a value in every output pipe """
        if len(self.out_pipe_list) == 0 and item is not None:
            raise Exception("Unable to put message because there is no output pipe:\n"+self.name)
        self.current_out_index = 0
        for conn, label in self.out_pipe_list:
            if item is not None:
                self.put_item_count += 1
            self.timed_send(item)
            self.current_out_index += 1

    def add_sender(self, connection, label):
        self.out_pipe_list.append((connection, label))

    def add_receiver(self, connection, label):
        self.in_pipe_list.append((connection, label))

    def setup_control_receiver(self, receiver):
        self.control_receiver = receiver

    def setup_control_sender(self, sender):
        self.control_sender = sender

    def _check_control_pipe(self):
        if self.control_receiver.poll():
            cmd = self.control_receiver.recv()
            if cmd == "status":
                name = ('{:>35}'.format(self.name))
                get_count = (' | Get {:>8}'.format(self.get_item_count))
                put_count = (' | Put {:>8}'.format(self.put_item_count))
                execution_time = float(("%0.2f" % self.execution_time))
                put_count = (' | Exec. {:>8}s'.format(execution_time))
                count = self.put_item_count
                if count == 0:
                    count = self.get_item_count
                if execution_time:
                    ips = count / execution_time
                    ips = int(self.loop_count / self.execution_time)
                    ips = ' | {:>10} i/s '.format('{:,}'.format(ips))
                else:
                    ips = ''
                self.control_sender.send(name + get_count + put_count + ips)

    def refresh_status(self):
        current_time = time()
        if self.start_time is None:
            self.start_time = current_time
        self.elapsed_time = current_time - self.start_time
        self._check_control_pipe()

    def set_stop_on_error(self, value):
        self._stop_on_error = value

    def report_status(self, message):
        # Silent internal plugins
        msg = ('{:>35}'.format(self.name))
        self.control_sender.send(msg + " --- " + message)

    def report(self, message):
        self.control_sender.send(message)

    def _close_descendents(self):
        self.put_all(None)

    def apply_config(self, config):
        """ Apply configuration to module """
        self._config.update(config)
