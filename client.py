import socket
import utils
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys
import os
import time


def on_created(event):
    print("on_created")
    utils.send_file(event.src_path, server_sock)


def on_deleted(event):
    print("on_deleted")
    utils.send_delete_file(event.src_path, server_sock)


def on_modified(event):
    print("on_modified")
    utils.send_delete_file(event.src_path, server_sock)
    utils.send_file(event.src_path, server_sock)


def on_moved(event):
    print("on_moved")
    utils.send_delete_file(event.src_path, server_sock)
    utils.send_file(event.dest_path, server_sock)


SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])+utils.getnum()
FOLDER_PATH = sys.argv[3]
BASE_PATH = utils.norming_path("\\").join(FOLDER_PATH.split(utils.norming_path("\\"))[:-1])
UPDATING_FREQUENCY = int(sys.argv[4])
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.connect((SERVER_IP, SERVER_PORT))

def main():
    if len(sys.argv) > 5:  # already connected
        client_id = sys.argv[5]
        server_sock.send(("ID " + client_id.decode()).encode())  # send id to server
        utils.execute_operation(FOLDER_PATH, server_sock)  # get the updates from the server
    else:
        server_sock.send("give id".encode())  # send id (to get one) and the path to track
        client_id = server_sock.recv(4096).decode()
        print("client recieved id: " +client_id)
        #time.sleep(1000)
        utils.send_file_deep(FOLDER_PATH, server_sock, BASE_PATH)
    time.sleep(1000)
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
    # try:
    print("starting whiloop")
    while True:
        time.sleep(UPDATING_FREQUENCY)
        server_sock.send((("update " + client_id).encode()))
        utils.execute_operation(FOLDER_PATH, server_sock)  # get the updates from the server
    # except:
    #     my_observer.stop()
    #     print("exeption")
    my_observer.join()

if __name__ == '__main__':
    main()