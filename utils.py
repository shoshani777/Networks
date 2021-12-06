import socket
import os
import sys
import server
import string

def getnum():
    return 18

def execute_operation(current_path, sock, address):
    print("execute_operation "+ current_path)
    log = []
    familiar = True
    text = ""
    while familiar:  # loop until done, update etc...
        familiar = False
        text += sock.recv(4096).decode()  # get operation
        print("went through recieving, text: "+text)
        if text.startswith("create_folder"):  # create folder
            familiar = True
            folder_path = text.split(" ", 2)[1]  # get the path
            try:
                os.makedirs(os.path.normpath(current_path + "\\" + folder_path))
                # create the directory (if exist do nothing)
            finally:
                log.append(text.split(" ", 2)[0]+" "+text.split(" ", 2)[1])  # add to log the operation create folder
                text = text.replace(text.split(" ")[0]+" "+text.split(" ")[1],"")  # remove create folder from text
        elif text.startswith("create_file"):  # create file
            familiar = True
            folder_path = text.split(" ", 2)[1]  # get the path
            if len(text.split(" ", 2)) > 2:  # part of the bytes of the file was sent to us
                file_text = text.split(" ", 2)[2]  # ([operation, path, text])
            else:
                file_text = ""
            with open(os.path.normpath(current_path + "\\" + folder_path), 'wb') as file:  # open file to write
                file_text += sock.recv(4096).decode()  # add the next bytes
                text += file_text
                while "#endoffunctions#" not in file_text:
                    file_text += sock.recv(4096).decode()
                    text += file_text
                file_text = file_text.split("#endoffunctions#", 1)[0]  # now file_text = only the file bytes
                log.append(("create_file " + folder_path + " " + file_text + "#endoffunctions#"))
                text = text.replace("create_file " + folder_path + " "+file_text+"#endoffunctions#","",1)
                file.write(file_text)
        elif text.startswith("delete"):
            familiar = True
            try:
                os.remove(text.split(" ", 2)[1])
            finally:
                log.append("delete " + (text.split(" ", 2)[1]))
                text.replace("delete " + text.split(" ", 2)[1],"",1)
        else:
            update(text)
    return log


#random ID choosing
def make_ID():
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(128))
    return password

def send_file(path, sock,base_folder):
    path_to_send = path.replace(norming_path(base_folder+"\\"),"",1)
    print("sending file "+ path_to_send)
    if os.path.isdir(path):
        print("creating folder "+ path_to_send +" in "+path)
        sock.send(("create_folder " + path_to_send).encode())
        return
    sock.send(("create_file " + path_to_send + " ").encode())  # first send the operation + path
    with open(path, 'rb') as file:
        sock.send(file.read())
        sock.send("#endoffunctions#".encode())


def send_delete_file(path, sock):
    sock.send(("delete " + path + " ").encode())

def send_file_deep(path, sock, base_folder):
    send_file(path, sock,base_folder)
    if(os.path.isdir(path)):
        for file in os.listdir(path):
            send_file_deep(file, sock,base_folder)

def norming_path(path):
    if(sys.platform.startswith("win")):
        return path.replace("/","\\")
    elif(sys.platform.startswith("linux")):
        return path.replace("\\", "/")