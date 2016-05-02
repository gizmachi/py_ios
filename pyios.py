import socket, select, string, sys, thread, time
from socket import inet_ntoa
from struct import pack

def thread_send(s):
    while True:
        msg = sys.stdin.readline()
        s.send(msg + "\r\n")

def thread_rec(threadname, s):
    while True:
        data = s.recv(4096)
        if not data :
            print 'Connection closed'
            sys.exit()
        else :
            sys.stdout.write(data)
        
def cidr2ddn(mask):
    bits = 0xffffffff ^ (1 << 32 - mask) - 1
    return inet_ntoa(pack('>I', bits))

def setupSocket():    
    host = sys.argv[1]
    port = int(sys.argv[2])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(100000)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()
     
    print 'Connected to remote host'

    socket_list = [s]
    read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
    ThreadName = "sending_thread"

    rt = thread.start_new_thread(thread_rec, (ThreadName, s))
    return s

### MACROs
def macro_save(s):
    s.send("end" + "\r\n")
    s.send("copy run start" + "\r\n")
    s.send("\r\n")

def macro_interface(s, inf, ip, mask="24"):
    if len(mask) < 7:
        mask = cidr2ddn(mask)
    
    s.send("conf t" + "\r\n")
    s.send("interface " + interface + "\r\n")
    s.send("ip address " + ipaddr + " " + netmask + "\r\n")
    s.send("no shutdown" + "\r\n")
    macro_save(s)


#main function
if __name__ == "__main__":
     
    if(len(sys.argv) < 3) :
        print 'Usage : python telnet.py hostname port'
        sys.exit()

    s = setupSocket()


    while True:
        line = sys.stdin.readline()
        splitline = line.split()
        if len(splitline) > 0 :
            if splitline[0] == "kill":
                print "exiting..."
                sys.exit()
            elif splitline[0] == 'macro':
                if len(splitline) == 2:
                    print "No marco specified!"
                if splitline[1] == 'int':
                    if len(splitline) == 5:
                        macro_interface(s, splitline[2], splitline[3],splitline[4])
                    elif len(splitline) == 4:
                        macro_interface(s, splitline[2], splitline[3])
                    else:
                        print "wrong nr of arguments!"
            else:
                s.send(line + "\r\n")
        else:
            s.send(line + "\r\n")
            



