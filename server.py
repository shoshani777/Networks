import socket
import sys
import string
import random
import os
import utils

SERVER_PORT = int(sys.argv[1])
IP_and_port_to_ID=dict()
IP_and_port_to_actions_nissing = dict()
BASE_PATH = os.path.normpath(".\\clients")

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
        result_str = utils.execute_operation(BASE_PATH, client_socket, IP_and_port_to_ID[client_address])
        for string in result_str:
            if (string.startswith("update ")):
                update(client_socket, IP_and_port_to_ID[client_address],client_address[0], client_address[1])
                client_socket.send("done " + IP_and_port_to_ID[client_address])
                break
            elif (string.startswith("give ")):
                ID = make_ID()
                IP_and_port_to_ID[client_address] = ID
                IP_and_port_to_actions_nissing[client_address] = []
                client_socket.send(IP_and_port_to_ID[client_address].encode())
                break
            elif (string.startswith("ID ")):
                ID = string.split(' ')[1]
                IP_and_port_to_ID[client_address] = ID
                if (len(os.listdir(os.path.normpath(BASE_PATH+"\\"+ID)))>0):
                    for file in os.listdir(os.path.normpath(BASE_PATH+"\\"+ID)):
                        utils.send_file_deep(os.path.normpath(BASE_PATH+"\\"+ID+"\\"+file),client_socket,ID)
                    client_socket.send("done "+ID)
                    IP_and_port_to_actions_nissing[client_address] = []
                client_socket.send("done " + ID)
                break
            else:
                ID = IP_and_port_to_ID[client_address]
                for address in IP_and_port_to_actions_nissing.keys():
                    if(IP_and_port_to_ID[address]!=ID and address!=client_address):
                        IP_and_port_to_actions_nissing[client_address].append(string)


if __name__ == '__main__':
    main()

