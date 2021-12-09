import socket
import os
import sys
import string
import random


def send_delete_file(path):
    return "delete " + path + "#endoffunctions#"


def execute_log(current_path, sock):
    log = []
    text = ""
    while text != "#endoflog#":
        while "#endoffunctions#" not in text and text != "#endoflog#":
            text += sock.recv(4096).decode()  # get operation
        if text.startswith("create_folder"):  # create folder
            action = text.split("#endoffunctions#", 1)[0]
            folder_path = action.split(" ", 1)[1]  # get the path
            try:
                os.makedirs(norming_path(current_path + "\\" + folder_path))
                log.append("create_folder " + folder_path + " #endoffunctions#")  # add to log the operation create folder
            finally:
                text = text.split("#endoffunctions#", 1)[1]
        elif text.startswith("create_file"):  # create file
            action = text.split("#endoffunctions#", 1)[0]
            folder_path = action.split("#startoftext#", 1)[0].split(" ",1)[1]  # get the path
            file_text = action.split("#startoftext#", 1)[1]  # ([operation, path, text])
            if os.path.exists(norming_path(current_path + "\\" + folder_path)):
                text = text.split("#endoffunctions#", 1)[1]
                continue
            with open(norming_path(current_path + "\\" + folder_path), 'wb') as file:  # open file to write
                log.append(action + "#endoffunctions#")
                text = text.split("#endoffunctions#", 1)[1]
                file.write(file_text.encode())
        elif text.startswith("delete"):
            action = text.split("#endoffunctions#", 1)[0]
            folder_path = action.split(" ", 1)[1]  # get the path
            if os.path.exists(norming_path(current_path + "\\" + folder_path)):
                log.append(send_delete_file(folder_path))
            folder_path = norming_path(current_path + "\\" + folder_path)
            deep_remove(folder_path)
            text = text.split("#endoffunctions#", 1)[1]
    return log


def send_log(log, sock):
    log.append("#endoflog#")
    for operation in log:
        sock.send(operation.encode())


# random ID choosing
def make_ID():
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(128))
    return password


def send_file(path, current_path):
    if os.path.isdir(norming_path(current_path + "\\" + path)):
        return "create_folder " + path + "#endoffunctions#"
    operation = "create_file " + path + "#startoftext#"  # first send the operation + path
    with open(norming_path(current_path + "\\" + path), 'rb') as file:
        operation += file.read().decode()
        operation += "#endoffunctions#"
    return operation


def send_file_deep(path, current_path):
    log = [send_file(path, current_path)]
    if os.path.isdir(norming_path(current_path + "\\" + path)):
        for file in os.listdir(norming_path(current_path + "\\" + path)):
            log.extend(send_file_deep(norming_path(path + "\\" + file), current_path))
    return log


def norming_path(path):
    if sys.platform.startswith("win"):
        return path.replace("/", "\\")
    elif sys.platform.startswith("linux"):
        return path.replace("\\", "/")


def deep_remove(absolute_path):
    if os.path.isdir(absolute_path):
        for file in os.listdir(absolute_path):
            deep_remove(norming_path(absolute_path + "\\" + file))
        try:
            os.rmdir(absolute_path)
        finally:
            pass
    else:
        try:
            os.remove(absolute_path)
        finally:
            pass
