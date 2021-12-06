import socket
import sys
import string
import random
import os
import utils

SERVER_PORT = int(sys.argv[1])+utils.getnum()
IP_and_port_to_ID=dict()
IP_and_port_to_actions_nissing = dict()
BASE_PATH = utils.norming_path(".\\clients")

#random ID choosing
def make_ID():
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(128))
    return password

#updating a client
def update(sock, ID, client_IP,client_port):
    for action in IP_and_port_to_actions_nissing[(client_IP,client_port)]:
        sock.send(action.encode())
    IP_and_port_to_actions_nissing[(client_IP, client_port)] = []


def main():
    if(not os.path.isdir(BASE_PATH)):
        os.mkdir(BASE_PATH)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', SERVER_PORT))
    server.listen(5)
    while True:
        client_socket, client_address = server.accept()

        if(client_address in IP_and_port_to_ID.keys()):
            ID = IP_and_port_to_ID[client_address]
            result_str = utils.execute_operation(utils.norming_path(BASE_PATH+"\\"+ID), client_socket)
        else:
            result_str = utils.execute_operation(BASE_PATH, client_socket)
        for string in result_str:
            if (string.startswith("update")):
                update(client_socket, IP_and_port_to_ID[client_address],client_address[0], client_address[1])
                client_socket.send("#endoffunctions#".encode())
                break
            elif (string.startswith("give id")):
                ID = make_ID()
                IP_and_port_to_ID[client_address] = ID
                IP_and_port_to_actions_nissing[client_address] = []
                client_socket.send(IP_and_port_to_ID[client_address].encode())
                os.mkdir(utils.norming_path(BASE_PATH+"\\"+ID))
                break
            elif (string.startswith("ID")):
                ID = string.split(' ')[1]
                IP_and_port_to_ID[client_address] = ID
                if (len(os.listdir(os.path.normpath(BASE_PATH+"\\"+ID)))>0):
                    for file in os.listdir(os.path.normpath(BASE_PATH+"\\"+ID)):
                        all_path = os.path.normpath(BASE_PATH+"\\"+ID+"\\"+file)
                        utils.send_file_deep(all_path,client_socket,os.path.normpath(BASE_PATH+"\\"+ID))
                    IP_and_port_to_actions_nissing[client_address] = []
                client_socket.send("#endoffunctions#".encode())
                break
            elif(string != ""):
                ID = IP_and_port_to_ID[client_address]
                for address in IP_and_port_to_actions_nissing.keys():
                    if(IP_and_port_to_ID[address]!=ID and address!=client_address):
                        IP_and_port_to_actions_nissing[client_address].append(string)
        client_socket.close()

if __name__ == '__main__':
    main()