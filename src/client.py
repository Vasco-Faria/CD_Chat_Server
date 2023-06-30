"""CD Chat client program"""
import fcntl
import logging
import os
import sys
import socket
import selectors

from src.protocol import CDProto, CDProtoBadFormat, TextMessage           

HOST='localhost'            #host do servidor
PORT=5555                   #porta do servidor

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)


class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        self.username=name                      #nome do usuario
        self.channel=None                       #canal
        self.csock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)         #socket do cliente
        self.addr=((HOST,PORT))                         #endereco do servidor
        self.selec=selectors.DefaultSelector()          #seletor de eventos
        pass

    def connect(self):
        """Connect to chat server and setup stdin flags."""
        self.csock.connect(self.addr)                           #conecta ao servidor
        self.selec.register(self.csock,selectors.EVENT_READ,self.read)              #registra o socket do cliente no seletor de eventos
        print(f"Connected to the server as {self.username}")                    #imprime a mensagem de conexao
        
        message=CDProto.register(self.username)                                 #
        CDProto.send_msg(self.csock,message)                                    #envia a mensagem de registro para o servidor
        pass
    
    def read(self,conn,mask):
        
        message=CDProto.recv_msg(self.csock)
        logging.debug('received "%s',message)
        
        if message != None:
            if (message.command=="message"):
                print(f"{message.message}")
            elif(message.command=="join"):
                print(f"\nNow in channel : {message.channel}")
            elif(message.command=="register"):
                print(f"\nNow connected as: {message.user}")

        

            
            
    def got_keyboard_data(self,stdin,mask):
        
        input=stdin.read().strip()                    #le a entrada do teclado
        
            
        if input.startswith("exit"):                          #se a entrada for exit
            self.csock.close()                              #fecha o socket do cliente
            sys.exit(f"\nUser {self.username} has left the chat. Bye!")               #fecha o programa
            
        elif input.startswith("/join"):                                  #se a entrada for join
            self.channel=input.split()[1]                                   #pega o nome do canal
            message=CDProto.join(self.channel) 
            CDProto.send_msg(self.csock,message) 
            print(f'Now in channel {self.channel}')
            
        else:                
            if self.channel:
                message=CDProto.message(input,self.channel)                             #cria a mensagem de texto      
                CDProto.send_msg(self.csock,message)                                                      #envia a mensagem para o servidor
            else:
                message=CDProto.message(input)                             #cria a mensagem de texto      
                CDProto.send_msg(self.csock,message)                                                      #envia a mensagem para o servidor
            

        

    def loop(self):
        """Loop indefinetely."""
        
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)                                     
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)
        
        self.selec.register(sys.stdin,selectors.EVENT_READ,self.got_keyboard_data)              #registra o teclado no seletor de eventos
        
        while True:
            sys.stdout.write('')       
            sys.stdout.flush()        
            for key,mask in self.selec.select():
                callback=key.data                                   #pega o callback
                callback(key.fileobj,mask)                          #callback