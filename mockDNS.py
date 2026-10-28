
#mockDNS.py


from socket import *
from netTools import *
from threading import *


def getHosts():
    hostFile = open("hosts.txt","r")
    hostDict  = {}

    for line in hostFile:
        line = line.strip()
        key,value,status = line.split(",")
        hostDict[key] = value,status

    hostFile.close()
    return hostDict

def updateHosts(hosts):
    hostFile = open("hosts.txt","w")
    print("Updating")
    
    for entry in hosts:
        print(entry+","+hosts[entry][0]+","+hosts[entry][1], file=hostFile, sep = "")

    hostFile.close()

def processRequest(cs, addr, hosts, lock):

    print ("Connnection from " + str(addr))
    try:
        msg = getMessage(cs)
        print(msg)

        (rID,ip) = msg.split(",")
        
        print("id: " + rID +"\nip: "+ip)
        print (addr[0])

        if (ip == addr[0]):
            status = "verified"
        else:
            status = "unsafe"
        lock.acquire()
        if rID not in hosts:
            print("Not Found")
            hosts[rID] = ip, status
            updateHosts(hosts)
        if status == "verified":
            if hosts[rID][1] == "unsafe":
                print("Updating status")
                hosts[rID] = ip,status
                updateHosts(hosts)
        lock.release()

        sendMessage(cs, "ok:"+status)
        where = ""
        while where == "":
            where = getMessage(cs).strip()
            print("*"+where[:6]+"*")
                
            if where[:6] == "where ":
                where = where[6:]
                msg = ""
                if where == "all":
                    for ID in hosts:
                        msg += ID + ","+str(hosts[ID])+"\n"
                elif where in hosts:
                    print(hosts[where][0])
                    msg = str(hosts[where][0])+","+str(hosts[where][1])
                else:
                    msg = "unknown,unknown"

                sendMessage(cs, msg)
                print("Returned: "+ msg)
            elif where[:2] == "ok":
                cs.close()
            else:
                print("Bad  Protocol")
                sendMessage(cs,"Bad  Protocol")
                cs.close()



                
    except ConnectionResetError:
        print("Connection from ",addr, "reset")


def mockDNSServer():

    lock = Lock()
    hosts = getHosts()
    port = 2001
    serversocket = socket(AF_INET, SOCK_STREAM)
    serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    host = getIPAddress()
    print("Listening on ", host)
    
    serversocket.bind((host, port))
    serversocket.listen(5)
    while True:
        print("Waiting")
        cs,addr = serversocket.accept()
        Thread(target=processRequest, args=(cs, addr, hosts, lock)).start()

          
mockDNSServer()
