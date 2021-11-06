import socket,sys
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(10)
    packet_data_text_len = 90
    port_num = int(sys.argv[1])
    ip_num = sys.argv[2]
    file_name = sys.argv[3]
    file = open("./"+file_name+".txt")
    alltext = file.read()
    textleft = alltext
    j=0
    index_to_text_dict = {}
    acknowledged_correctly = set([])
    while(textleft != None):
        j=j+1
        if(len(textleft)>packet_data_text_len):
            curr_text = textleft[:packet_data_text_len]
            textleft = textleft[packet_data_text_len:]
        else:
            curr_text = textleft
            textleft = None
        index_to_text_dict[j]=str(j)+":"+curr_text
    max_value = j
    index_to_text_dict[max_value] = "max"+index_to_text_dict[max_value]
    while(acknowledged_correctly!=set(index_to_text_dict.keys())):
        diff = set(index_to_text_dict.keys()).difference(acknowledged_correctly)
        for i in diff:
            s.sendto(index_to_text_dict[i].encode(),(ip_num,port_num))
        timedout = False
        try:
            while True:
                data, addr = s.recvfrom(100)
                colon_place = data.decode().find(":")
                num = data.decode()[:colon_place]
                if(num.__contains__("max")):
                    num = num[3:]
                if(index_to_text_dict[int(num)]==data.decode()):
                    acked_num = int(num)
                    if(acked_num not in acknowledged_correctly):
                        acknowledged_correctly.add(acked_num)
        except:
            continue
except:
    print("Input error")
finally:
    s.close()