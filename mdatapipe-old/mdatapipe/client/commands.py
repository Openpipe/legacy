try:
    from pip._internal import main as pip_main
except ImportError:
    from pip import main as pip_main

import click
import colorama
from time import sleep
from mdatapipe.core.pipeline import PipelineInfo, Pipeline
from mdatapipe.client.colorhelper import print_info

colorama.init()


@click.command()        # NOQA
@click.argument('file', type=click.Path(exists=False), nargs=-1, required=True)
@click.option('--fail', '-f', is_flag=True)
@click.option('--stats-interval', '-s', type=int)
@click.option('--parallel', '-p', multiple=True)
@click.option('--silent', is_flag=True)
def run(file, fail, stats_interval, parallel, silent):

    pipeline_list = []

    # Load all pipelines
    for filename in file:
        if not silent:
            print_info("Loading pipeline", filename)
        pipeline = Pipeline(file=filename, parallel=parallel, silent=silent)
        pipeline_list.append(pipeline)

    # Start all pipelines
    for pipeline in pipeline_list:
        pipeline.start(fail)

    time_to_status = stats_interval

    # Loop checking the stats of all pipelines
    total_processes = 1  # Dummy value to start the collect stats loop

    try:
        while total_processes > 0:
            if time_to_status:
                time_to_status -= 1
            total_processes = 0
            for pipeline in pipeline_list:
                reques_status = (time_to_status == 0)
                if reques_status:
                    pipeline.check_status(reques_status, verbose=True)
                    time_to_status = stats_interval
                pipeline_processes = pipeline.get_active_count()
                total_processes += pipeline_processes
                pipeline.check_status(reques_status, verbose=True)
            sleep(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        for pipeline in pipeline_list:
            pipeline.kill()


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
