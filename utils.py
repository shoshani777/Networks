import socket
import os


def execute_operation(current_path, sock, client_id):
    text = sock.recv(4096)  # get operation + path (if needed)
    if text.startswith("create_folder"):  # create folder
        folder_path = text.split(" ")[1]  # get the path
        try:
            os.makedirs(os.path.normpath(current_path + "\\" + folder_path))
            # create the directory (if exist do nothing)
        finally:
            pass
    elif text.startswith("create_file"):  # create file
        folder_path = text.split(" ", 2)[1]  # get the path
        if len(text.split(" ", 2)) > 2:  # part of the bytes of the file was sent to us
            file_text = text.split(" ", 2)[2]  # ([operation, path, text])
        else:
            file_text = b""
        with open(os.path.normpath(current_path + "\\" + folder_path), 'w') as file:  # open file to write
            file_text += sock.recv(100)  # add the next text
            while bytes("end " + client_id) not in text:
                file_text += sock.recv(100)
            text += file_text
            file_text = file_text.removesuffix(bytes("end " + client_id))
            file.write(str(file_text))
    elif text.startswith("delete"):
        os.remove(text.split(" ")[1])
    elif text.startswith("done"):
        return None
    return text


def send_file(path, sock, client_id):
    if os.path.isdir(path):
        sock.send(bytes("create_folder " + path))
        return
    sock.send("create_file " + path + " ")  # first send the operation + path
    with open(path, 'r') as file:
        for line in file:
            sock.send(line)  # send line by line
        sock.send(bytes("end " + client_id))


def send_delete_file(path, sock):
    sock.send("delete " + path)


clso = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
execute_operation("", clso, "1j1j")
send_file("", clso, "1j1j")
send_delete_file("", clso)
