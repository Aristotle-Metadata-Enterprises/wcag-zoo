import click
import os
from wcag_zoo.utils import get_wcag_class


class Zookeeper(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(os.path.join(os.path.dirname(__file__), 'validators')):
            if (
                filename.endswith('.py') and
                not filename.startswith('_') and
                not filename.startswith('.')
            ):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        cmd = get_wcag_class(name)
        return cmd.as_cli()


@click.command(cls=Zookeeper)
def zookeeper():
    """
    Zookeeper collates all of the WCAG-Zoo commands into a single command line tool to limit
    collision with other commands.
    """
    pass


if __name__ == "__main__":
    zookeeper()
