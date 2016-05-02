import socket, select, string, sys, thread, time
from socket import inet_ntoa
from struct import pack

## Some default parameters
default_netmask = "24"
default_username = "josef"
default_password = "cisco"
default_domain = "example.com"

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
    bits = 0xffffffff ^ (1 << 32 - int(mask)) - 1
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

def macro_interface(s, interface, ipaddr, mask=default_netmask):
    if len(mask) < 7:
        mask = cidr2ddn(int(mask))
    
    s.send("conf t" + "\r\n")
    s.send("interface " + interface + "\r\n")
    s.send("ip address " + ipaddr + " " + mask + "\r\n")
    s.send("no shutdown" + "\r\n")
    macro_save(s)

def macro_setup(s):
    s.send("conf t" + "\r\n")
    s.send("no ip domain-lookup" + "\r\n")
    s.send("service password-encryption" + "\r\n")
    s.send("enable secret " + default_password + "\r\n")
    s.send("username " + default_username + " privilege 15 secret " + default_password + "\r\n")
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

            # Exit
            if splitline[0] == "kill":
                print "exiting..."
                sys.exit()

            # Macro
            elif splitline[0] == 'macro':
                if len(splitline) == 2:
                    print "No marco specified!"

                # Setup interface with IPv4 address
                if splitline[1] == 'int':
                    if len(splitline) == 5:
                        macro_interface(s, splitline[2], splitline[3],splitline[4])
                    elif len(splitline) == 4:
                        macro_interface(s, splitline[2], splitline[3])
                    else:
                        print "wrong nr of arguments!"

                # setup some default settings for device
                elif splitline[1] == 'setup':
                    macro_setup(s)

                # Save running configuration to startup configuration
                elif splitline[1] == 'save':
                    macro_save(s)

                # specific macro not found
                else:
                    print "MACRO NOT IMPLEMENTED!"

            # Regular command line
            else:
                s.send(line + "\r\n")
        
        # Empty newline
        else:
            s.send(line + "\r\n")
            



