import click

from ml import patches
from ml.cmd.train import train
from ml.cmd.preprocess import preprocess
from ml.cmd.monitor import monitor
from ml.cmd.util import util
from ml.cmd.evaluate import evaluate
from ml.cmd.data import data
from ml.cmd.tmp import tmp


@click.group()
def cli():
    patches.apply()


cli.add_command(train)
cli.add_command(preprocess)
cli.add_command(monitor)
cli.add_command(util)
cli.add_command(evaluate)
cli.add_command(data)
cli.add_command(tmp)

if __name__ == '__main__':
    cli()