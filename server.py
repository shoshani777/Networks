import socket
import sys
import string
import random
import os
import utils

SERVER_PORT = int(sys.argv[1])+utils.getnum()
ID_to_clientIDs=dict()
clientID_to_actionLog = dict()
BASE_PATH = utils.norming_path(".\\clients")


def main():
    if(not os.path.isdir(BASE_PATH)):
        os.mkdir(BASE_PATH)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', SERVER_PORT))
    server.listen(5)
    while True:
        client_socket, client_address = server.accept()
        msg = client_socket.recv(4096).decode()
        action = msg.split(" ")[0]
        clientID = msg.split(" ")[1]
        was_give_id,was_update,was_ID = False,False,False
        if (action == "give_id"):
            was_give_id = True
            ID = utils.make_ID()
            ID_to_clientIDs[ID] = [].append(clientID)
            clientID_to_actionLog[clientID] = []
            client_socket.send(ID)
            os.mkdir(utils.norming_path(BASE_PATH + "\\" + ID))
        elif (action == "ID"):
            was_ID = True
            ID = msg.split(' ')[2]
            ID_to_clientIDs[ID].append(clientID)
            clientID_to_actionLog[clientID] = []
            if(len(os.listdir(utils.norming_path(BASE_PATH + "\\" + ID)))==0):
                utils.send_log([])
            else:
                for file in os.listdir(utils.norming_path(BASE_PATH + "\\" + ID)):
                    utils.send_log(utils.send_file_deep(file,utils.norming_path(BASE_PATH + "\\" + ID)),client_socket)
        elif(action == "update"):
            ID = msg.split(' ')[2]
            was_update = True
            utils.send_log(clientID_to_actionLog[clientID],clientID)
        if(not was_ID):
            log = utils.execute_log(utils.norming_path(BASE_PATH + "\\" + ID),client_socket)
            if(was_update):
                for act in log:
                    for curr_clientID in ID_to_clientIDs[ID]:
                        if(curr_clientID!=clientID):
                            clientID_to_actionLog[curr_clientID].append(act)
        client_socket.close()

if __name__ == '__main__':
    main()