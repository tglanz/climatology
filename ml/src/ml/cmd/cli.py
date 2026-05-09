import click

from ml.cmd.train import train
from ml.cmd.preprocess import preprocess
from ml.cmd.monitor import monitor
from ml.cmd.util import util
from ml.cmd.evaluate import evaluate


@click.group()
def cli():
    pass


cli.add_command(train)
cli.add_command(preprocess)
cli.add_command(monitor)
cli.add_command(util)
cli.add_command(evaluate)

if __name__ == '__main__':
    cli()