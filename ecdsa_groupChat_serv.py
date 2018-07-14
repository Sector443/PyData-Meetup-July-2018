import socket
import select
import sys
import threading
import nacl.utils
from nacl.public import PrivateKey, SealedBox
from nacl.encoding import Base64Encoder
import os, fnmatch
import base64

#Server intialization [start]
def check_keys(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(name)
    return result

if check_keys('*Key.txt', os.getcwd()) == []:
    print("[Server keys not found, generating fresh keys]")
    serv_priv_key = PrivateKey.generate()
    encoded_priv_key = serv_priv_key.encode(encoder=Base64Encoder)
    serv_pub_key = serv_priv_key.public_key
    encoded_pub_key = serv_pub_key.encode(encoder=Base64Encoder)
    f = open("serv_privKey.txt", "w")
    f.write(encoded_priv_key)
    f.close
    f = open("serv_pubKey.txt", "w")
    f.write(encoded_pub_key)
    f.close()

def read_priv_key():
    f = open("serv_privKey.txt", "r")
    priv_key = PrivateKey(f.readline(), encoder=Base64Encoder)
    f.close()
    return priv_key

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
 
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.bind((IP_address, Port))
server.listen(200)
list_of_clients = []
#Server intialization [end]

def clientthread(conn, addr):
    conn.send("=>[Welcome to PyData encrypted chatroom]<= \n made by CJHackerz@Sector443")
    
    while True:
            try:
                encrypted_msg = conn.recv(2048)
                unseal_box = SealedBox(read_priv_key())
                message = unseal_box.decrypt(encrypted_msg)
                if message:
                    print ("<" + addr[0] + "> " + message)
                    message_to_send = "<" + addr[0] + "> " + message
                    broadcast(message_to_send, conn)
 
                else:
                    remove(conn)
            except:
                continue
 
def broadcast(message, connection):
    for clients in list_of_clients:
        if clients!=connection:
            try:
                clients.send(message)
            except:
                clients.close()
                remove(clients)
 
def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)
 
while True:
    conn, addr = server.accept()
    list_of_clients.append(conn)
    print(addr[0] + " connected")
    
    if conn.recv(2048) == "AUTHREQ":
        f = open("serv_pubKey.txt", "r")
        pub_key = f.readline()
        f.close()
        print("Sending public key: " + pub_key)
        conn.send(pub_key)

    threading.Thread(target=clientthread,args=(conn, addr))    
 
conn.close()
server.close()
