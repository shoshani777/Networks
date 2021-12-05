from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys
import time
# SERVER_IP = sys.argv[1]
# SERVER_PORT = int(sys.argv[2])
# FOLDER_PATH = sys.argv[3]
# UPDATING_FREQUENCY = sys.argv[4]


def on_created(event):
    print("was created: "+event.src_path)
def on_deleted(event):
    print("was deleted: "+event.src_path)
def on_modified(event):
    print("was modified: "+event.src_path)
def on_moved(event):
    print("was moved from: "+event.src_path + " to: " + event.dest_path)

#client connecting to server, sending or recieving data
patterns = ["*"]
ignore_patterns = None
ignore_directories = False
case_sensitive = True
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

path = "C:\\python_files\\new"
go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)
my_observer.start()
try:
    while True:
        time.sleep(5)
except:
    my_observer.stop()
my_observer.join()
