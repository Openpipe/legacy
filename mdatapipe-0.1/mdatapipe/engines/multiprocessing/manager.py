from mdatapipe.engines.base.manager import PipelineManagerBase
from multiprocessing.connection import wait, Pipe
from time import time


class PipelineManager(PipelineManagerBase):

    def loop(self):  # NOQA: C901
        self.exit_msg = ''
        check_for_events = True

        while check_for_events:

            event_handlers = list(self.event_handlers)
            if self.receiver:
                event_handlers.append(self.receiver)

            if len(event_handlers) == 0:
                break

            input_conn_list = wait(event_handlers)
            for conn in input_conn_list:
                if conn == self.receiver:
                    item = conn.recv()
                    if item is None:
                        self.receiver = None
                    else:
                        self.on_input_func(item)
                    continue
                event = conn.recv()
                event_label = self.event_manager_to_plugin(conn)
                if __debug__:
                    self.logger.debug("GOT %s FROM %s", event, event_label)
                if event == "started":
                    self.on_started(event_label)
                if event is None:   # Got "None" event - plugin was terminated
                    exit_msg = conn.recv()
                    self.on_exit(event_label, exit_msg)
                    self.remove_event_source(conn)
                if event == "error":
                    return 1, "Error"

        print(self.exit_msg)
        return 0, "Finished"

    def on_started(self, event_label):
        self.started_count += 1
        if self.started_count == len(list(self.all_plugins)):
            self.send_start_item()

    def on_exit(self, event_label, exit_msg):
        if exit_msg is not None:
            self.exit_msg += "%s stats:\n" % event_label.instance_id
            for item in exit_msg:
                self.exit_msg += "\t %s: [Clk: %s] [CPU: %s] [COUNT: %d]" % (
                    item['label'], item['clk_time'], item['cpu_time'], item['count']
                    )
                self.exit_msg += "\n"

    def start(self):
        """ start all processes """
        # The process needs to be started so that setup runs in the new pid
        for control_manager in self.control_managers:
            control_manager.send("start")

    def send_start_item(self):

        # We send and item followed by None
        first_step = list(self.all_steps)[0]
        for plugin in first_step[1]:
            control_manager = self.control_manager(plugin)
            control_manager.send("item")
            control_manager.send(time())
            control_manager.send("item")
            control_manager.send(None)

    def setup(self):
        """ start all processes """
        # The process needs to be started so that setup runs in the new pid
        for control_manager in self.control_managers:
            control_manager.send("setup")

    def terminate(self):
        for control_manager in self.control_managers:
            control_manager.send("terminate")

    def connect(self, plugin1, plugin2, extra_label=''):
        """ create plugin1 output to plugin2 input """

        receiver, sender = Pipe(duplex=False)

        connection = (plugin2.instance_id, sender)
        control_manager = self.control_manager(plugin1)

        control_manager.send("output " + extra_label)
        control_manager.send(connection)

        connection = (plugin1.instance_id, receiver)
        control_manager = self.control_manager(plugin2)
        control_manager.send("input")
        control_manager.send(connection)

    def on_input(self, func):
        *_, last = self.all_steps   # Get the last step
        receiver, sender = Pipe(duplex=False)
        for plugin in last[1]:
            connection = ("Manager", sender)
            control_manager = self.control_manager(plugin)
            control_manager.send("output")
            control_manager.send(connection)
        self.receiver = receiver
        self.on_input_func = func
