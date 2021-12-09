import socket
import sys
import os
import utils

SERVER_PORT = int(sys.argv[1])
ID_to_clientIDs = dict()
clientID_to_actionLog = dict()
# initialize
BASE_PATH = utils.norming_path(".\\clients")
# the base path (where the server keeps the folders) is relative to this folder in clients (new folder)


def main():
    if not os.path.isdir(BASE_PATH):  # if clients not exist create one
        os.mkdir(BASE_PATH)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', SERVER_PORT))
    server.listen(5)  # server initialization
    while True:
        client_socket, client_address = server.accept()  # accept client
        msg = client_socket.recv(4096).decode()  # receive the request (update, id, give id)
        action = msg.split(" ")[0]  # the client message is action personal_id id (optional)
        clientID = msg.split(" ")[1]
        was_give_id, was_update, was_ID = False, False, False
        if action == "give_id":  # the client asks for id
            was_give_id = True
            ID = utils.make_ID()  # generate id
            print(ID)  # print id
            ID_to_clientIDs[ID] = []  # initialize the value of this id for client id's for this client id
            ID_to_clientIDs[ID].append(clientID)
            clientID_to_actionLog[clientID] = []  # empty log (no updates)
            client_socket.send(ID.encode())  # send client the id
            os.mkdir(utils.norming_path(BASE_PATH + "\\" + ID))  # create folder for him
        elif action == "ID":  # already has id
            was_ID = True
            ID = msg.split(' ')[2]
            ID_to_clientIDs[ID].append(clientID)
            clientID_to_actionLog[clientID] = []
            if len(os.listdir(utils.norming_path(BASE_PATH + "\\" + ID))) == 0:
                utils.send_log([])
            else:
                for file in os.listdir(utils.norming_path(BASE_PATH + "\\" + ID)):
                    utils.send_log(utils.send_file_deep(file, utils.norming_path(BASE_PATH + "\\" + ID)), client_socket)
        elif action == "update":  # ask for update, give updates, execute his updates, update all action logs
            ID = msg.split(' ')[2]
            was_update = True
            utils.send_log(clientID_to_actionLog[clientID], client_socket)
        if not was_ID:
            log = utils.execute_log(utils.norming_path(BASE_PATH + "\\" + ID), client_socket)
            if was_update:
                for act in log:
                    for curr_clientID in ID_to_clientIDs[ID]:
                        if curr_clientID != clientID:
                            clientID_to_actionLog[curr_clientID].append(act)
        client_socket.close()


if __name__ == '__main__':
    main()
