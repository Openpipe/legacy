"""
    The PipelineBaseclass provides the pipeline core management class that can be used by python applictions to embed
    their own code based pipelines.
"""
from multiprocessing import Pipe
from time import time
from os import getenv
from collections import OrderedDict


class PipelineBase(object):

    def __init__(self, config=None, save_results=False):
        self.config = config
        self.blocks = OrderedDict()
        self.out_pipe_list = []  # Needed to unblock the first step
        self.in_pipe_list = []   # Needed for save_results
        self.current_input_index = 0
        self.debug = getenv("DEBUG")
        self.save_results = save_results
        self.result_data = []
        self.name = "Pipeline"  # Needed for compatibility with the plugin get/put

    def start(self, stop_on_error=True, verbose=False):

        # Setup control pipes
        self._setup_control_pipes()

        # Setup pipes between plugins
        self._setup_data_pipes()
        self._setup_group_pipes()

        #  self.vprint("Starting pipeline")
        self.start_time = time()
        for block_name, all_steps in self.blocks.items():
            for current_step in all_steps:
                for process in current_step:
                    process.set_stop_on_error(stop_on_error)
                    process.start()
                #  self.vprint('{:>50} , PID {}'.format(info(process.desc), info(process.pid)))

        # Unblock the first step
        self.put_all(self.start_time)

        # Terminate input
        self.put_all(None)

    def _setup_control_pipes(self):
        """ Setup pipes between step/processes """
        self.control_sender_list = []
        self.control_receiver_list = []

        for block_steps in self.blocks.values():
            for current_step in block_steps:
                for current_process in current_step:
                    receiver, sender = Pipe(duplex=False)
                    current_process.setup_control_receiver(receiver)
                    self.control_sender_list.append(sender)

                    receiver, sender = Pipe(duplex=False)
                    current_process.setup_control_sender(sender)
                    self.control_receiver_list.append(receiver)

    def _setup_data_pipes(self):
        """ Setup pipes between steps/processes """

        # Setup connection between the pipeline manager and the first step
        for process in self.blocks['start'][0]:
            receiver, sender = Pipe(duplex=False)
            self.add_sender(sender, process.name)
            process.add_receiver(receiver, self.name)

        # Setup links between consecutive steps
        for block_steps in self.blocks.values():
            for i in range(len(block_steps) - 1):
                current_step = block_steps[i]
                next_step = block_steps[i+1]
                for current_process in current_step:
                    for next_process in next_step:
                        receiver, sender = Pipe(duplex=True)
                        # Senders from this step, are connected
                        # to receivers in the next step
                        current_process.add_sender(sender, next_process.name)
                        next_process.add_receiver(receiver, current_process.name)

    def _setup_group_pipes(self):

        # Setup links to reference pipelines
        # Loop all blocks
        for block_name, block_steps in self.blocks.items():
            next_step = block_steps[0]
            # Find references to it
            for all_steps in self.blocks.values():
                for current_step in all_steps:
                    for current_process in current_step:
                        for next_process in next_step:
                            if block_name in getattr(current_process, 'pipeline_references', []):
                                receiver, sender = Pipe(duplex=False)
                                current_process.set_group_reference(block_name, sender)
                                next_process.add_receiver(receiver, current_process.name)

        # Setup output of every block
        for block_name, steps in self.blocks.items():
            for process in steps[-1]:
                if block_name == 'start' and self.save_results:
                    receiver, sender = Pipe(duplex=False)
                    process.add_sender(sender, self.name)
                    self.add_receiver(receiver, process.name)
                    continue
                process.set_null_output(True)

    def add_sender(self, connection, label):
        self.out_pipe_list.append((connection, label))

    def add_receiver(self, connection, label):
        self.in_pipe_list.append((connection, label))

    def get(self):
        """
            Get one element from the input pipes, using round-robin
            If all pipes are closed, raise an EOFError
        """
        get_item = None
        get_conn = len(self.in_pipe_list) > 0   # Only get if there are connections available
        while get_conn:
            current_in_conn, current_in_label = self.in_pipe_list[self.current_input_index]
            self.current_in_conn = current_in_conn
            self.current_in_label = current_in_label

            # Rotate the current input pipe selection
            self.current_input_index += 1
            if self.current_input_index >= len(self.in_pipe_list):
                self.current_input_index = 0

            item = current_in_conn.recv()
            if self.debug:
                print("GOT FROM %s: %s" % (self.current_in_label, str(item)))

            if item is None:
                # Delete current connection from list
                new_in_pipe_list = [conn for conn in self.in_pipe_list if conn != current_in_conn]
                self.in_pipe_list = new_in_pipe_list
                self.current_input_index = 0
                get_conn = len(self.in_pipe_list) > 0
            else:
                get_item = item
                get_conn = False

        return get_item

    def get_active_count(self):
        active_processes = 0
        for steps in self.blocks.values():
            for step in steps:
                for process in step:
                    if process.is_alive():
                        active_processes += 1
        return active_processes

    def kill(self):
        """ Kill all plugin processes """
        for steps in self.blocks.values():
            for step in steps:
                for process in step:
                    process.terminate()

    def add_step(self, block_name, step):
        block_steps = self.blocks.get(block_name, [])
        block_steps.append(step)
        self.blocks[block_name] = block_steps

    def wait_end(self, verbose=False):
        result = None
        if self.save_results:
            while True:
                value = self.get()
                if value is None:
                    return
                self.result_data.append(value)

        while self.get_active_count() > 0:
            result = self.check_status(verbose)
            if not result:  # A plugin failed
                break

        return result

    def run(self):
        self.start()
        self.wait_end()

    def check_status(self, request_status=False, verbose=False):

        if request_status:
            for conn in self.control_sender_list:
                conn.send("status")
            if verbose:
                print("-" * 40, self.file)

        for conn in self.control_receiver_list:
            while conn.poll():
                result = conn.recv()
                if result is None:  # A plugin failed
                    self.kill()
                    return False
                if not self.silent and verbose:
                    print(result)
        return True

    def put_all(self, item):
        """ Put a value in every output pipe """
        if self.debug:
            print("%s PUTALL: %s" % ("PipeLine", str(item)))
        if len(self.out_pipe_list) == 0 and item is not None:
            raise Exception("Unable to put message because there is no output pipe:\n"+self.name)
        for conn, label in self.out_pipe_list:
            conn.send(item)
