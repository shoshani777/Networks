import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
namesAndIDs = 'Ori Shoshani - 214776163, Gilad Hananel - 324291327'
s.sendto(namesAndIDs.encode(), ('127.0.0.1', 12345))
data, addr = s.recvfrom(1024)
if data.decode()!=namesAndIDs:
    print("server client connection failed.")
s.close()