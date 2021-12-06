import socket
import os


def execute_operation(current_path, sock):
    print("execute_operation "+ current_path)
    log = []
    familiar = True
    text = "".encode()
    while familiar:  # loop until done, update etc...
        familiar = False
        text += sock.recv(4096)  # get operation
        if text.startswith("create_folder".encode()):  # create folder
            familiar = True
            folder_path = text.split(" ".encode(), 2)[1]  # get the path
            try:
                os.makedirs(os.path.normpath(current_path + "\\" + (folder_path).decode()))
                # create the directory (if exist do nothing)
            finally:
                log.append((text.removesuffix(text.split(b" ", 2)[2].encode())).decode())  # add to log the operation create folder
                text = text.split(" ".encode(), 2)[2]  # remove create folder from text
        elif text.startswith("create_file".encode()):  # create file
            familiar = True
            folder_path = text.split(" ".encode(), 2)[1]  # get the path
            if len(text.split(" ".encode(), 2)) > 2:  # part of the bytes of the file was sent to us
                file_text = text.split(" ".encode(), 2)[2]  # ([operation, path, text])
            else:
                file_text = "".encode()
            with open(os.path.normpath(current_path + "\\" + folder_path), 'wb') as file:  # open file to write
                file_text += sock.recv(4096)  # add the next bytes
                text += file_text
                while "#endoffunctions#".encode() not in file_text:
                    file_text += sock.recv(4096)
                    text += file_text
                file_text = file_text.split("#endoffunctions#".encode(), 1)[0]  # now file_text = only the file bytes
                log.append(("create_file " + folder_path.decode() + " ").encode() + file_text + "#endoffunctions#".encode())
                text = text.removeprefix(("create_file " + folder_path.decode() + " ").encode()+file_text+"#endoffunctions#".encode())
                file.write(file_text)
        elif text.startswith("delete".encode()):
            familiar = True
            try:
                os.remove(text.split(" ".encode(), 2)[1])
            finally:
                log.append("delete " + (text.split(" ".encode(), 2)[1]).decode())
                text.removeprefix(("delete " + text.split(b" ", 2)[1].decode()).encode())
        else:
            log.append(text.decode())
    return log


def send_file(path, sock):
    print("sending file "+ path)
    if os.path.isdir(path):
        print("creating folder "+ path)
        sock.send(("create_folder " + path).encode())
        return
    sock.send(("create_file " + path + " ").encode())  # first send the operation + path
    with open(path, 'rb') as file:
        sock.send(file.read())
        sock.send("#endoffunctions#".encode())


def send_delete_file(path, sock):
    sock.send(("delete " + path + " ").encode())

def send_file_deep(path, sock):
    send_file(path, sock)
    if(os.path.isdir(path)):
        for file in os.listdir(path):
            send_file_deep(file, sock)
