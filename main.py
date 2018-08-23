import os
import shutil
import time
from multiprocessing import Process

import click

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


@click.command(short_help="start child watchers for folder tree")
@click.option('--target', '-t', default='.', type=click.Path(exists=True, file_okay=False))
@click.option('--archive', '-a', default='./archive', type=click.Path(exists=False, file_okay=False))
def start(target, archive):

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

    for directory in dirs_to_monitor:

        absolute_process = os.path.join(target_path, directory)
        absolute_archive = os.path.join(archive, directory)

        click.secho(
            "Dispatching monitor for `%s`" % directory,
            fg='green')

        watcher = Process(target=monitor, args=(absolute_process, absolute_archive))
        watcher.start()
        running_monitors.append(watcher)

    for proc in running_monitors:
        proc.join()


def monitor(target, archive):
    """Watch over a target folder and process csv files in it one by one.
    Once processed, files will be moved to the archive folder
    """

    if not os.path.exists(archive):
        os.makedirs(archive)

    to_process_queue = {
        os.path.join(target, file)
        for file
        in os.listdir(target)
        if not os.path.isdir(file) and file.endswith(".csv")}

    class CsvHandler(PatternMatchingEventHandler):
        patterns = ["*.csv"]

        def process(self, event):
            if event.is_directory:
                return

            click.echo("New file detected at %s" % event.src_path)

            to_process_queue.add(os.path.join(target, event.src_path))

        def on_modified(self, event):
            pass

        def on_created(self, event):
            self.process(event)

    click.secho(
        "Monitoring `%s`" % target,
        fg='green')

    observer = Observer()
    observer.schedule(CsvHandler(), path=target)
    observer.start()

    from elasticsearch import Elasticsearch

    es = Elasticsearch()

    try:
        while True:
            while to_process_queue:
                file = next(iter(to_process_queue))
                click.secho(
                    "Processing `%s`..." % file,
                    fg='green')
                shutil.move(file, os.path.join(archive, os.path.basename(file)))
                to_process_queue.remove(file)
                click.secho(
                    "Processed `%s` successfully and moved to `%s`" % (target, archive),
                    fg='green')

            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == '__main__':
    start()
