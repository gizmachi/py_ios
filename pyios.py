import socket, select, string, sys, thread, time
from socket import inet_ntoa
from struct import pack

## Some default parameters
default_netmask = "24"
default_username = "josef"
default_password = "cisco"
default_domain = "example.com"


class config:
    hostname = None
    socket = None

    def __init__(self, name):
        self.hostname = name


class device:
    hostname = None
    idnr = None
    def __init__(self, id):
        self.hostname = "NAME_NOT_SET"
        self.idnr = id



def thread_send(s):
    while True:
        msg = sys.stdin.readline()
        s.send(msg + "\r\n")

def thread_rec(conf, s):
    while True:
        data = s.recv(4096)
        if not data :
            print 'Connection closed'
            sys.exit()
        else :
            sys.stdout.write(data)
            if "hostname" in data:
                conf.hostname = data.split()[-1]

        
def cidr2ddn(mask):
    bits = 0xffffffff ^ (1 << 32 - int(mask)) - 1
    return inet_ntoa(pack('>I', bits))

def setupSocket(conf, host=None, port=None):
    if host == None:    
        host = sys.argv[1]
    if port == None:
        port = int(sys.argv[2])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(100000)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        #sys.exit()
        return None

    #print 'Connected to remote host'

    socket_list = [s]
    read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
    ThreadName = "sending_thread"

    rt = thread.start_new_thread(thread_rec, (conf, s))
    return s

def connect():
    print "looking for GNS devices..."

    devices = []

    conf = config("NAME_NOT_SET")
    address = "localhost"
    port = 2000
    dev_id = 1

    while True:
        sock = setupSocket(conf, address, port)
        if sock is not None:
            newDevice = device(dev_id)
            newDevice.socket = sock
            devices.append(newDevice)
            port += 1
            dev_id += 1
        else:
            #print "Found " + str(len(devices)) + " running devices."
            return devices



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
     
    #if(len(sys.argv) < 3) :
    #    print 'Usage : python telnet.py hostname port'
    #    sys.exit()

    conf = config("NAME_NOT_SET")
    #s = setupSocket(conf)
    dev = connect()

    if len(dev) > 0:
        print "Found " + str(len(dev)) + " running devices.."
        s = dev[0].socket
    else:
        print "No devices found"
        sys.exit()

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
                if len(splitline) == 1:
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

                elif splitline[1] == 'hostname':
                    print "Hostname: " + conf.hostname + "\n"

                # specific macro not found
                else:
                    print "MACRO NOT IMPLEMENTED!"

            # Regular command line
            else:
                s.send(line + "\r\n")
        
        # Empty newline
        else:
            s.send(line + "\r\n")
            



