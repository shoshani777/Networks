import socket
import utils
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys
import time


def on_created(event):
    log.extend(utils.send_file_deep(event.src_path, BASE_PATH))


def on_deleted(event):
    log.append(utils.send_delete_file(event.src_path))


def on_modified(event):
    log.append(utils.send_delete_file(event.src_path))
    log.extend(utils.send_file_deep(event.src_path, BASE_PATH))


def on_moved(event):
    log.append(utils.send_delete_file(event.src_path))
    log.extend(utils.send_file_deep(event.des_path, BASE_PATH))


SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])+utils.getnum()
FOLDER_PATH = sys.argv[3]
BASE_PATH = utils.norming_path("\\").join(FOLDER_PATH.split(utils.norming_path("\\"))[:-1])
UPDATING_FREQUENCY = int(sys.argv[4])
log = []
personal_id = utils.make_ID()


def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect((SERVER_IP, SERVER_PORT))
    if len(sys.argv) > 5:  # already connected
        ID = sys.argv[5]
        server_sock.send(("ID " + personal_id + " " + ID).decode().encode())
        utils.execute_log(BASE_PATH, server_sock)  # get the updates from the server
    else:
        server_sock.send(("give_id " + personal_id).encode())
        ID = server_sock.recv(4096).decode()  # send current file
        log.extend(utils.send_file_deep("", BASE_PATH))
        utils.send_log(log, server_sock)
        log.clear()
    server_sock.close()
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
    while True:
        time.sleep(UPDATING_FREQUENCY)
        server_sock.connect((SERVER_IP, SERVER_PORT))
        server_sock.send(("update " + personal_id + " " + ID).encode())
        utils.execute_log(BASE_PATH, server_sock)
        utils.send_log(log, server_sock)
        server_sock.close()
        log.clear()


if __name__ == '__main__':
    main()
