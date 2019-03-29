from mdatapipe.engines.base.plugin import PipelinePluginBase
from mdatapipe.core.statistics import StatsRecord
import cProfile
import pstats
import io
from os import environ


class PipelinePlugin(PipelinePluginBase):

    def init(self, instance_id=None):
        self.is_profiling = environ.get("MDP_PROFILE", False)
        self.exit_code = 0  # Used to identify the plugin "exit" status
        self._put_total_size = 0
        self.out_count = 0
        if __debug__:
            if self.is_profiling:
                self.cProfile = cProfile.Profile()
            else:
                self._stats_on_input = StatsRecord('Execution')

    def load(self):
        return None, None   # Dummy control/event handlers

    def put(self, obj):
        self.out_count += 1
        if __debug__:
            #  self._put_total_size += total_size(obj)
            if self.is_profiling:
                self.cProfile.disable()
            else:
                self._stats_on_input.pause()
        if len(self.current_output_list) > 0:  # No output was added
            label, connection = next(self.current_output_list_cycle)
            if __debug__:
                self.logger.debug("put_to %s %s %s", label, connection, obj)
            success = connection._on_input(obj)
            assert(success == 0)

        for extra_label, connections in list(self.get_all_connections(self.ConnType.EXTRA_OUTPUT)):
            # TODO: Cycle on output connections
            connection, label = list(connections.items())[0]
            if __debug__:
                self.logger.debug("put_to_extra %s %s %s %s", extra_label, label, connection, obj)
            success = connection._on_input(obj)
            assert(success == 0)

        if __debug__:
            if self.is_profiling:
                self.cProfile.enable()
            else:
                self._stats_on_input.resume()

    def put_all(self, obj):

        output_connections = list(self.get_all_connections(self.ConnType.OUTPUT))

        try:
            for label, connection in output_connections:
                if __debug__:
                    self.logger.debug("%s put_all %s %s %s", self.instance_id, label, connection, obj)
                connection._on_input(obj)

            for extra_label, connections in list(self.get_all_connections(self.ConnType.EXTRA_OUTPUT)):
                for connection, label in connections.items():
                    if __debug__:
                        self.logger.debug("put_all_extra %s %s %s", extra_label, label, obj)
                    connection._on_input(obj)
        except KeyboardInterrupt:
            exit(1)

    def _on_input(self, item):
        if __debug__:
            if self.is_profiling:
                self.cProfile.enable()
            else:
                self._stats_on_input.start()
        if __debug__:
            self.logger.debug("GOT INPUT %s", item)
        self.config = self._dynaconf.render(item)
        try:
            self.on_input(item)
        except KeyboardInterrupt:
            raise
        except:  # NOQA: E722
            self._execution_error(item)

            return False

        # Pass-ahead transport handling
        if self.is_transport:
            self.put(item)

        if __debug__:
            if self.is_profiling:
                self.cProfile.disable()
            else:
                self._stats_on_input.stop()

        return 0

    def _execution_error(self, item):
        execution_id = getattr(self, "execution_id", self.instance_id)
        msg = (
            "---------- Plugin %s execution failed, for source item (%d) ----------:"
            % (execution_id, self.get_item_count))
        self.logger.exception(str(item) + "\n" + msg)
        self.exit_msg = msg
        self.exit_code = 1

    def terminate(self):
        pass    # There is nothing to terminate when running on single thread

    def _get_stats(self):
        if self.is_profiling:
            s = io.StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(self.cProfile, stream=s).sort_stats(sortby)
            ps.print_stats()
            return s.getvalue()
        else:
            stats_dict = []
            stats_dict.append(self._stats_on_input.result())
            #  stats_dict.append({'label': 'size', 'size': sizeof_fmt(self._put_total_size)})
            stats_dict.append({'label': 'ocount', 'ocount': self.out_count})
            return stats_dict
