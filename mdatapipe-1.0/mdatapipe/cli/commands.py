import click
from mdatapipe.pipeline import Pipeline


@click.command()
@click.argument('filename', type=click.Path(exists=False), required=True)
def run(filename):
    """
    The run command is used to run a data pipeline.
    You must provide the filename of the YAML file describing the pipeline.
    """
    pipeline = Pipeline(filename)
    pipeline.load()
