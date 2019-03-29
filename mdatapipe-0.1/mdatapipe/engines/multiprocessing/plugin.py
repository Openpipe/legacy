import os
from multiprocessing import Process
from multiprocessing.connection import wait as multiprocessing_wait, Pipe
from mdatapipe.engines.base.plugin import PipelinePluginBase
from mdatapipe.core.statistics import StatsRecord


class PipelinePlugin(PipelinePluginBase):

    def init(self, instance_id=None):
        # Create the process object that will be used to run the plugin
        self.process = Process(target=self._run, name=instance_id)
        if __debug__:
            self._stats_on_input = StatsRecord('Execution')
            self._stats_recv = StatsRecord('Retrieval')
            self._stats_put = StatsRecord('Delivery ')

    def load(self):
        control_receiver, control_sender = Pipe(duplex=False)
        events_receiver, events_sender = Pipe(duplex=False)
        self.add_control_connection(control_receiver, "Manager")
        self.add_events_connection(events_sender, "Manager")

        # Start the process, this will call  _run()
        self.process.start()

        return control_sender, events_receiver

    def put(self, obj):

        if __debug__:
            if not self.is_transport:
                self._stats_on_input.pause()

            self._stats_put.start()

        if len(self.current_output_list) > 0:  # Only when outputs are availabe
            label, connection = next(self.current_output_list_cycle)
            self.logger.debug("put_to %s %s %s", label, connection, obj)
            connection.send(obj)

        for extra_label, connections in list(self.get_all_connections(self.ConnType.EXTRA_OUTPUT)):
            # TODO: Cycle on output connections
            connection, label = list(connections.items())[0]
            self.logger.debug("put_to_extra %s %s %s %s", extra_label, label, connection, obj)
            connection.send(obj)

        if __debug__:
            self._stats_put.stop()

            if not self.is_transport:
                self._stats_on_input.resume()

    def put_all(self, obj):

        output_connections = list(self.get_all_connections(self.ConnType.OUTPUT))

        for label, connection in output_connections:
            self.logger.debug("put_all %s %s", label, obj)
            connection.send(obj)

        for extra_label, connections in list(self.get_all_connections(self.ConnType.EXTRA_OUTPUT)):
            for connection, label in connections.items():
                self.logger.debug("put_all_extra %s %s %s", extra_label, label, obj)
                connection.send(obj)

    def _run(self):

        self._send_event("control")  # Ready to receive control commands

        while True:
            if self.state == self.State.STARTED:
                wait_type = "data_or_control"
                connection_check_list = self.connection_check_list
            else:  # If not started only deal with control connections
                wait_type = "control"
                connection_check_list = self.controls
            self.logger.debug(
                'wait_%s %d %s %s',
                wait_type, os.getpid(), self.state, connection_check_list
            )

            for connection in multiprocessing_wait(connection_check_list, None):
                if connection in self.inputs:
                    self._on_input(connection)
                elif connection in self.controls:
                    self._on_control(connection)
                else:
                    raise Exception     # Unmanaged connection !?

    def _on_control(self, connection):
        item = connection.recv()
        self.logger.debug("GOT CONTROL %s", item)
        assert(isinstance(item, str))
        command_args = item.split()
        command_args[0] = command_args[0].lower()
        control_func = getattr(self, '_control_'+command_args[0])
        control_func(connection, *command_args[1:])

    def _on_input(self, connection):  # NOQA: C901
        if __debug__:
            self._stats_recv.start()
        item = connection.recv()
        if __debug__:
            self._stats_recv.stop()
            self.logger.debug("GOT INPUT %s %s", item, connection)
        if item is None:
            if __debug__:
                self._stats_recv.rollback()
            self.del_input_connection(connection)
            connection.close()
            if len(list(self.inputs)) == 0:
                self.logger.debug("Terminating on 0 inputs: %s", self.inputs)
                self.exit()
                self.put_all(None)      # Terminate all dependent plugins
                self._control_terminate(None)
                exit(0)
            else:  # A connection was closed
                return
        self.config = self._dynaconf.render(item)
        # Pass-ahead of transport handling
        if self.is_transport:
            self.put(item)
        try:
            if __debug__:
                self._stats_on_input.start()
            self.on_input(item)
            if __debug__:
                self._stats_on_input.stop()
        except KeyboardInterrupt:
            exit()
        except:  # NOQA: E722
            self._execution_error(item)

    def _execution_error(self, item):
        execution_id = getattr(self, "execution_id", self.instance_id)
        msg = (
            "---------- Plugin %s execution failed, for source item (%d) ----------:"
            % (execution_id, self.get_item_count))
        self.logger.exception(str(item) + "\n" + msg)
        self._send_event("error")

    def _send_event(self, msg):
        """ Send an event message to all events connections """
        for label, connection in self.conn_list[self.ConnType.EVENTS].items():
            self.logger.debug("send_event %s %s %s", label, connection, msg)
            connection.send(msg)

    def _control_item(self, control_connection, *args):
        """ Received a "start" control command """
        self._on_input(control_connection)

    def _control_start(self, control_connection, *args):
        """ Received a "start" control command """
        self.state = self.State.STARTED
        self.start()
        self._send_event("started")

    def _control_setup(self, control_connection, *args):
        """ Received a "setup" control command """
        self.setup()
        self._send_event("setup")

    def _control_terminate(self, control_connection, *args):
        """ Received a "terminate" control command """
        self.state = self.State.TERMINATED
        self._send_event(None)
        if __debug__:
            stats = self._get_stats()
            self._send_event(stats)
        else:
            self._send_event(None)
        exit(1)

    def _control_output(self, control_connection, *args):
        """ Received an "output" command """
        label, connection = control_connection.recv()
        if len(args) == 1:
            self.add_extra_output_connection(args[0], connection, label)
        else:
            self.add_output_connection(connection, label)

    def _control_input(self, control_connection, *args):
        """ Received an "output" command """
        label, connection = control_connection.recv()
        self.add_input_connection(connection, label)

    def terminate(self):

        # Auto-kill, only used by the start plugin
        self._control_terminate(self, None)

    def _get_stats(self):
        stats_dict = []
        stats_dict.append(self._stats_put.result())
        stats_dict.append(self._stats_recv.result())
        stats_dict.append(self._stats_on_input.result())
        return stats_dict
