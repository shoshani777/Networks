import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = int(sys.argv[1])
s.bind(('', port))
got = {}
flag_got_max = False
was_printed = False
max_value = 0
while True:
    data, address = s.recvfrom(100)
    data = data.decode()
    to_send = data
    data = data.split(':', 1)
    if data[0].startswith("max"):
        data[0] = data[0][3:]
        max_value = int(data[0])
        flag_got_max = True
    got[int(data[0])] = data[1]
    s.sendto(to_send.encode(), address)
    if (flag_got_max and not was_printed):
        if ((set([i for i in range(1, max_value + 1)])==set(got.keys()))):
            for key in range(1, max_value + 1):
                print(got[key], end="")
            was_printed = True