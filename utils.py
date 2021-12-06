import socket
import os
import sys
import string


def getnum():
    return 18


def send_delete_file(path):
    return "delete " + path + " #endoffunctions#"


def execute_log(current_path, sock):
    log = []
    text = ""
    while text is not "#endoflog#":
        while "#endoffunctions#" not in text:
            text += sock.recv(4096).decode()  # get operation
        if text.startswith("create_folder"):  # create folder
            folder_path = text.split(" ", 2)[1]  # get the path
            try:
                os.makedirs(norming_path(current_path + "\\" + folder_path))
                log.append("create_file " + folder_path + " #endoffunctions#")  # add to log the operation create folder
            finally:
                text = text.replace("create_file " + folder_path + " #endoffunctions#", "", 1)
        elif text.startswith("create_file"):  # create file
            folder_path = text.split(" ", 2)[1]  # get the path
            if os.path.exists(norming_path(current_path + "\\" + folder_path)):
                text = text.replace("create_file " + folder_path + " " + file_text + "#endoffunctions#", "", 1)
                continue
            file_text = text.split(" ", 2)[2]  # ([operation, path, text])
            with open(norming_path(current_path + "\\" + folder_path), 'w') as file:  # open file to write
                file_text = file_text.split("#endoffunctions#", 1)[0]  # now file_text = only the file bytes
                log.append(("create_file " + folder_path + " " + file_text + "#endoffunctions#"))
                text = text.replace("create_file " + folder_path + " " + file_text + "#endoffunctions#", "", 1)
                file.write(file_text)
        elif text.startswith("delete"):
            folder_path = text.split(" ", 2)[1]  # get the path
            if os.path.exists(folder_path):
                log.append(send_delete_file(folder_path))
            folder_path = norming_path(current_path + "\\" + folder_path)
            try:
                os.remove(folder_path)
            finally:
                text.replace("delete " + text.split(" ", 2)[1] + " #endoffunctions#", "", 1)
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
        return "create_folder " + path + " #endoffunctions#"
    operation = "create_file " + path + " "  # first send the operation + path
    with open(path, 'r') as file:
        operation += file.read()
        operation += "#endoffunctions#"
    return operation


def send_file_deep(path, current_path):
    log = [send_file(path, current_path)]
    if os.path.isdir(norming_path(current_path + "\\" + path)):
        for file in os.listdir(norming_path(current_path + "\\" + path)):
            log.extend(send_file_deep(file, norming_path(current_path + "\\" + path)))
    return log


def norming_path(path):
    if sys.platform.startswith("win"):
        return path.replace("/", "\\")
    elif sys.platform.startswith("linux"):
        return path.replace("\\", "/")
