import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = int(sys.argv[1])
s.bind(('', port))
got = {}
flag_got_max = False
max_value = 0
while True:
    data, address = s.recvfrom(100)
    data = data.split(b':', 1)
    if data[0].startswith(b"max"):
        data[0] = data[0][3:]
        max_value = int(data[0])
        flag_got_max = True
    got[int(data[0])] = data[1]
    s.sendto(b':'.join(data), address)
    if flag_got_max:
        got_all = True
        for index in range(1, max_value + 1):
            if index not in got.keys():
                got_all = False
        if got_all:
            break
sorted_keys = sorted(got.keys())
for key in sorted_keys:
    print(got[key], end="")

