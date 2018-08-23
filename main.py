import os
from string import Template
from multiprocessing import Process

import click

from monitor import monitor


@click.command()
@click.option('--target', '-t', default='.', type=click.Path(exists=True, file_okay=False))
@click.option('--archive', '-a', default='./archive', type=click.Path(exists=False, file_okay=False))
@click.option('--index', '-i', default='rows-$folder',
              help=("The target index name for the processed files, "
                    "can be also used as a template with `$folder` as the name of the originating subfolder."))
def start(target, archive, index):
    """A small folder watching tool that loads files into elastic search."""
    target_path = os.path.abspath(target)

    click.echo("Monitored folder is `%s`" % target_path)

    dirs_to_monitor = [
        directory
        for directory
        in os.listdir(target_path)
        if os.path.isdir(os.path.join(target_path, directory))]

    if not dirs_to_monitor:
        click.secho(
            "Could not find directories to monitor at `%s`" % target_path,
            fg='red')
        return

    if not os.path.exists(archive):
        os.makedirs(archive)

    running_monitors = []

    index_name_template = Template(index)

    for directory in dirs_to_monitor:

        absolute_process = os.path.join(target_path, directory)
        absolute_archive = os.path.join(archive, directory)
        index_name = index_name_template.safe_substitute(folder=directory)

        click.secho(
            "Dispatching monitor for `%s`, target index: `%s`" % (directory, index_name),
            fg='green')

        watcher = Process(target=monitor, args=(absolute_process, absolute_archive, index_name))
        watcher.start()

        running_monitors.append(watcher)

    for proc in running_monitors:
        proc.join()


if __name__ == '__main__':
    start()
