import socket
import utils
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys
import time
import os


# on create add to log the create operation + path
def on_created(event):
    relative_path = event.src_path.replace(utils.norming_path(BASE_PATH + "\\"), "", 1)
    log.append(utils.send_file(relative_path, BASE_PATH))


# on delete add to log the delete operation + path
def on_deleted(event):
    relative_path = event.src_path.replace(utils.norming_path(BASE_PATH + "\\"), "", 1)
    log.append(utils.send_delete_file(relative_path))


# on modified add to log delete path then create path
def on_modified(event):
    if not os.path.isdir(event.src_path):
        relative_path = event.src_path.replace(utils.norming_path(BASE_PATH + "\\"), "", 1)
        log.append(utils.send_delete_file(relative_path))
        log.append(utils.send_file(relative_path, BASE_PATH))


# on moved add to log delete path then create path in the new location
def on_moved(event):
    relative_path_src = event.src_path.replace(utils.norming_path(BASE_PATH + "\\"), "", 1)
    relative_path_dst = event.dest_path.replace(utils.norming_path(BASE_PATH + "\\"), "", 1)
    log.append(utils.send_delete_file(relative_path_src))
    log.append(utils.send_file(relative_path_dst, BASE_PATH))


SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
FOLDER_PATH = utils.norming_path(sys.argv[3])
BASE_PATH = utils.norming_path("\\".join(FOLDER_PATH.split(utils.norming_path("\\"))[:-1]))
MONITORED_FOLDER = FOLDER_PATH.replace(utils.norming_path(BASE_PATH + "\\"), "", 1)
UPDATING_FREQUENCY = int(sys.argv[4])
log = []
personal_id = utils.make_ID()  # get personal id to get only relevant for you updates
# initialisation


def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect((SERVER_IP, SERVER_PORT))  # connect to server
    if len(sys.argv) > 5:  # already has id
        ID = sys.argv[5]
        server_sock.send(("ID " + personal_id + " " + ID).encode())  # tell the server you have id (to get the folder)
        utils.execute_log(BASE_PATH, server_sock)  # get the updates from the server
    else:
        server_sock.send(("give_id " + personal_id).encode())  # ask the server for new id
        ID = server_sock.recv(4096).decode()  # recv id from server
        log.extend(utils.send_file_deep(MONITORED_FOLDER, BASE_PATH))  # add to operation log to create all the folder
        utils.send_log(log, server_sock)  # send the log
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
    # watchdog initialization
    while True:
        time.sleep(UPDATING_FREQUENCY)  # sleep for wanted time not to get updates (or send them)
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.connect((SERVER_IP, SERVER_PORT))  # reconnect the server
        server_sock.send(("update " + personal_id + " " + ID).encode())  # ask the server for update
        utils.execute_log(BASE_PATH, server_sock)  # execute the update
        time.sleep(1)
        utils.send_log(log, server_sock)  # send server your updates
        time.sleep(1)
        server_sock.close()  # disconnect the server, let someone else connect
        log.clear()


if __name__ == '__main__':
    main()
