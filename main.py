import os
import time
from subprocess import Popen

import click

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

ARCHIVE_FOLDER_NAME = 'archive'
TO_PROCESS_FOLDER = 'to_process'


@click.group()
def cli():
    pass


@click.command()
@click.option('--target', '-t', default='.')
def start(target):

    click.echo("Booting up")

    target_path = os.path.abspath(target)

    click.echo("Target folder is `%s`" % target_path)

    process_folder = os.path.join(target_path, TO_PROCESS_FOLDER)

    if not os.path.isdir(process_folder):
        click.secho(
            "Could not find processing directory at `%s`, might be missing or not a directory" % process_folder,
            fg='red')
        return

    dirs_to_monitor = [
        directory
        for directory
        in os.listdir(process_folder)
        if os.path.isdir(os.path.join(process_folder, directory))]

    if not dirs_to_monitor:
        click.secho(
            "Could not find directories to monitor at `%s`" % process_folder,
            fg='red')
        return

    archive_folder = os.path.join(target_path, ARCHIVE_FOLDER_NAME)

    running_monitors = []

    for directory in dirs_to_monitor:

        absolute_process = os.path.join(process_folder, directory)
        absolute_archive = os.path.join(archive_folder, directory)

        click.secho(
            "Dispatching monitor for `%s`" % directory,
            fg='green')

        running_monitors.append(
            Popen(['python', __file__, 'monitor', '-t', absolute_process, '-a', absolute_archive]))

    while running_monitors:
        for proc in running_monitors:
            retcode = proc.poll()
            if retcode is not None: # Process finished.
                running_monitors.remove(proc)
                break
            else:
                time.sleep(.1)
                continue


@click.command()
@click.option('--target', '-t')
@click.option('--archive', '-a')
def monitor(target, archive):
    class CsvHandler(PatternMatchingEventHandler):
        patterns = ["*.csv"]

        def process(self, event):
            """
            event.event_type
                'modified' | 'created' | 'moved' | 'deleted'
            event.is_directory
                True | False
            event.src_path
                path/to/observed/file
            """
            print(event.src_path, event.event_type)

        def on_modified(self, event):
            self.process(event)

        def on_created(self, event):
            self.process(event)

    click.secho(
        "Started monitoring `%s`" % target,
        fg='green')

    observer = Observer()
    observer.schedule(CsvHandler(), path=target)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


cli.add_command(start)
cli.add_command(monitor)

if __name__ == '__main__':
    cli()
