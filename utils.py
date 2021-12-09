import os
import sys
import string
import random


# return the formatted message for the other side to delete file
def send_delete_file(path):
    return "delete " + path + "#endoffunctions#"  # the format for delete operation


# get a log of operations and execute them all
def execute_log(current_path, sock):
    log = []
    text = ""
    while text != "#endoflog#":  # when end of log, finish
        while "#endoffunctions#" not in text and text != "#endoflog#":  # read until the full operation in text
            text += sock.recv(4096).decode()  # get operation
        if text.startswith("create_folder"):  # create folder
            action = text.split("#endoffunctions#", 1)[0]  # text = action#end...#...
            folder_path = action.split(" ", 1)[1]  # get the path
            try:
                os.makedirs(norming_path(current_path + "\\" + folder_path))
                log.append("create_folder " + folder_path + " #endoffunctions#")  # add to log the operation
            finally:
                text = text.split("#endoffunctions#", 1)[1]
        elif text.startswith("create_file"):  # create file
            action = text.split("#endoffunctions#", 1)[0]
            folder_path = action.split("#startoftext#", 1)[0].split(" ", 1)[1]  # get the path
            file_text = action.split("#startoftext#", 1)[1]  # ([operation, path, text])
            if os.path.exists(norming_path(current_path + "\\" + folder_path)):
                text = text.split("#endoffunctions#", 1)[1]
                continue
            with open(norming_path(current_path + "\\" + folder_path), 'w') as file:  # open file to write
                file.write(file_text)
            log.append(action + "#endoffunctions#")
            text = text.split("#endoffunctions#", 1)[1]
        elif text.startswith("delete"):  # delete
            action = text.split("#endoffunctions#", 1)[0]
            folder_path = action.split(" ", 1)[1]  # get the path
            if os.path.exists(norming_path(current_path + "\\" + folder_path)):
                log.append(send_delete_file(folder_path))
            folder_path = norming_path(current_path + "\\" + folder_path)
            deep_remove(folder_path)
            text = text.split("#endoffunctions#", 1)[1]
    return log


# get a log of operations, send them all + end of operations indicator
def send_log(log, sock):
    log.append("#endoflog#")  # add end of log
    for operation in log:
        sock.send(operation.encode())  # send the formatted operations


# random ID choosing
def make_ID():
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(128))  # random a list of 128 chars and numbers
    # join them to string
    return password


# return formatted operation of create file in path
def send_file(path, current_path):
    if os.path.isdir(norming_path(current_path + "\\" + path)):  # if directory (folder)
        return "create_folder " + path + "#endoffunctions#"  # return create file operation
    operation = "create_file " + path + "#startoftext#"  # else, file -> first send the operation + path
    with open(norming_path(current_path + "\\" + path), 'r') as file:
        operation += file.read()  # add the file text
    operation += "#endoffunctions#"  # format
    return operation


# return list of operations to create folder with file inside
def send_file_deep(path, current_path):
    log = [send_file(path, current_path)]  # send this file
    if os.path.isdir(norming_path(current_path + "\\" + path)):  # if folder
        for file in os.listdir(norming_path(current_path + "\\" + path)):  # for every file in folder
            log.extend(send_file_deep(norming_path(path + "\\" + file), current_path))
    return log


# norm the path based on operating system
def norming_path(path):
    if sys.platform.startswith("win"):
        return path.replace("/", "\\")
    elif sys.platform.startswith("linux"):
        return path.replace("\\", "/")


# remove file, if folder remove every file inside and then the folder
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
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
        finally:
            pass
