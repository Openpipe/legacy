import click
from mdatapipe.cli.commands import run


@click.group()
def cli():
    pass


cli.add_command(run)


def main():
    cli()


if __name__ == '__main__':
    main()
