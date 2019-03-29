from mdatapipe.client import commands
import click


@click.group()
def cli():
    pass


cli.add_command(commands.run)
cli.add_command(commands.installdeps)


def main():
    cli()


if __name__ == '__main__':
    main()
