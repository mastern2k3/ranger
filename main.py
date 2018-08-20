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


@click.command(short_help="start child watchers for folder tree")
@click.option('--target', '-t', default='.', type=click.Path(exists=True, file_okay=False))
def start(target):

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
            Popen(['python', __file__, 'monitor', absolute_process, absolute_archive]))

    while running_monitors:
        for proc in running_monitors:
            retcode = proc.poll()
            if retcode is not None: # Process finished.
                running_monitors.remove(proc)
                break
            else:
                time.sleep(.1)
                continue


@click.command(short_help="start monitoring a csv folder")
@click.argument('target', type=click.Path(exists=True, file_okay=False))
@click.argument('archive', type=click.Path(exists=False, file_okay=False))
def monitor(target, archive):
    """This command watches over a target folder and processes csv files in it one by one.
    Once processed files will be moved to the archive folder
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

    try:
        while True:
            while to_process_queue:
                file = next(iter(to_process_queue))
                click.secho(
                    "Processing `%s`..." % file,
                    fg='green')
                os.rename(file, os.path.join(archive, os.path.basename(file)))
                to_process_queue.remove(file)
                click.secho(
                    "Processed `%s` successfully and moved to `%s`" % (target, archive),
                    fg='green')

            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


cli.add_command(start)
cli.add_command(monitor)

if __name__ == '__main__':
    cli()
