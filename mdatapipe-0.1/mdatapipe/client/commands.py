try:
    from pip._internal import main as pip_main
except ImportError:
    from pip import main as pip_main

import click
import colorama
from .colorhelper import print_info
from ..core.engine import MDP_ENGINE
from ..core.pipeline import PipelineInfo, FilePipeline
from ..core.statistics import StatsRecord


colorama.init()


@click.command()        # NOQA
@click.argument('file', type=click.Path(exists=False), nargs=-1, required=True)
@click.option('--fail', '-f', is_flag=True)
@click.option('--stats-interval', '-s', type=int)
@click.option('--parallel', '-p', multiple=True)
@click.option('--silent', is_flag=True)
def run(file, fail, stats_interval, parallel, silent):

    pipeline_list = []

    execution_stats = StatsRecord('Execution')
    execution_stats.start()

    # Load all pipelines
    for filename in file:
        if not silent:
            print_info("Loading pipeline %s [%s]" % (filename, MDP_ENGINE))
        pipeline = FilePipeline(file=filename, parallel=parallel, silent=silent)
        pipeline_list.append(pipeline)

    # Start all pipelines
    for pipeline in pipeline_list:
        pipeline.start()

    try:
        exit_code, exit_message = pipeline.wait_end()

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    execution_stats.stop()

    if not silent:
        print("Full pipeline run:")
        item = execution_stats.result()
        print(
            "\t %s: [Clk: %s] [CPU: %s]" %
            (
                item['label'], item['clk_time'], item['cpu_time'],
            )
        )
    exit(exit_code)


@click.command()
@click.argument('file', type=click.Path(exists=True), nargs=-1, required=True)
def installdeps(file):

    # Load all pipelines
    for filename in file:

        print_info("Loading pipeline", filename)
        pipeline = PipelineInfo(file=filename)
        # Remove duplicates
        requires = set(pipeline.requires)
        missing = requires
        requires_str = ', '.join(missing)
        if not requires_str:
            print("No additional python packages are required.")
            return
        print_info("The following python packages are required:\n", requires_str)
        answer = None
        while answer not in ['Y', 'N']:
            answer = input("Install now? (Y/N)").upper()
        if answer == "N":
            return
        for package in missing:
            pip_main(['install', package])
