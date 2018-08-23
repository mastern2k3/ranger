import os
import shutil
import time
from datetime import datetime
import csv

import click

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError


def process(csv_file, index_name):

    es_connection = Elasticsearch()

    rows_processed = 0

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for line in reader:
            line['timestamp'] = datetime.now()
            try:
                remapped = {name.strip().replace(' ', '_'): val for name, val in line.items()}
                
                es_connection.index(index=index_name, doc_type='row', body=remapped)
                rows_processed += 1
            except RequestError as ex:
                click.secho("Exception: %s" % ex, fg='red', err=True)
                raise

    return rows_processed


def monitor(target, archive, index_name):
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

    try:
        while True:
            while to_process_queue:
                file = next(iter(to_process_queue))
                click.secho(
                    "Processing `%s`..." % file,
                    fg='green')
                rows_processed = process(file, index_name)
                shutil.move(file, os.path.join(archive, os.path.basename(file)))
                to_process_queue.remove(file)
                click.secho(
                    "Processed `%s` successfully, %s rows, and moved to `%s`" % (target, rows_processed, archive),
                    fg='green')

            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
