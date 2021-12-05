import socket
import os


def execute_operation(current_path, sock):
    log = []
    familiar = True
    while familiar:  # loop until done, update etc...
        familiar = False
        text = sock.recv(4096)  # get operation
        if text.startswith(b"create_folder"):  # create folder
            familiar = True
            folder_path = text.split(b" ", 2)[1]  # get the path
            try:
                os.makedirs(os.path.normpath(current_path + "\\" + str(folder_path)))
                # create the directory (if exist do nothing)
            finally:
                log.append(text.removesuffix(bytes(text.split(b" ", 2)[2])))  # add to log the operation create folder
                text = text.split(b" ", 2)[2]  # remove create folder from text
        if text.startswith(b"create_file"):  # create file
            familiar = True
            folder_path = text.split(b" ", 2)[1]  # get the path
            if len(text.split(b" ", 2)) > 2:  # part of the bytes of the file was sent to us
                file_text = text.split(b" ", 2)[2]  # ([operation, path, text])
            else:
                file_text = b""
            with open(os.path.normpath(current_path + "\\" + folder_path), 'wb') as file:  # open file to write
                file_text += sock.recv(4096)  # add the next bytes
                text += file_text
                while bytes("#endoffunctions#") not in file_text:
                    file_text += sock.recv(4096)
                    text += file_text
                file_text = file_text.split(bytes("#endoffunctions#"), 1)[0]  # now file_text = only the file bytes
                log.append(bytes("create_file " + folder_path + " ") + file_text + bytes("#endoffunctions#"))
                text = text.removeprefix(bytes("create_file " + folder_path + " ")+file_text+bytes("#endoffunctions#"))
                file.write(file_text)
        if text.startswith(b"delete"):
            familiar = True
            try:
                os.remove(text.split(b" ", 2)[1])
            finally:
                log.append("delete " + text.split(b" ", 2)[1])
                text.removeprefix("delete " + text.split(b" ", 2)[1])
    return log


def send_file(path, sock):
    if os.path.isdir(path):
        sock.send(bytes("create_folder " + path))
        return
    sock.send("create_file " + path + " ")  # first send the operation + path
    with open(path, 'rb') as file:
        sock.send(file.read())
        sock.send(bytes("#endoffunctions#"))


def send_delete_file(path, sock):
    sock.send(bytes("delete " + path + " "))
