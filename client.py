import socket
import utils
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys
import time


def on_created(event):
    utils.send_file(event.src_path, server_sock)


def on_deleted(event):
    utils.send_delete_file(event.src_path, server_sock)


def on_modified(event):
    utils.send_delete_file(event.src_path, server_sock)
    utils.send_file(event.src_path, server_sock)


def on_moved(event):
    utils.send_delete_file(event.src_path, server_sock)
    utils.send_file(event.dest_path, server_sock)


SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
FOLDER_PATH = sys.argv[3]
UPDATING_FREQUENCY = sys.argv[4]
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.connect((SERVER_IP, SERVER_PORT))


def main():
    if len(sys.argv) > 4:  # already connected
        client_id = sys.argv[5]
        server_sock.send(bytes("ID " + client_id))  # send id to server
        utils.execute_operation(FOLDER_PATH, server_sock)  # get the updates from the server
    else:
        server_sock.send(bytes("give id"))  # send id (to get one) and the path to track
        client_id = server_sock.recv(4096)


    patterns = ["*"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved

    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, FOLDER_PATH, recursive=go_recursively)
    my_observer.start()
    try:
        while True:
            time.sleep(5)
            server_sock.send(bytes("update " + client_id))
            utils.execute_operation(FOLDER_PATH, server_sock)  # get the updates from the server
    except:
        my_observer.stop()
    my_observer.join()

if __name__ == '__main__':
    main()