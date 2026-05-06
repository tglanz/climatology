import click

from ml.cmd.train import train
from ml.cmd.preprocess import preprocess
from ml.cmd.monitor import monitor


@click.group()
def cli():
    pass


cli.add_command(train)
cli.add_command(preprocess)
cli.add_command(monitor)
