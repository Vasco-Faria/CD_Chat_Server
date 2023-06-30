"""CD Chat server program."""
import logging
import socket 
import selectors

from src.protocol import CDProto,CDProtoBadFormat            


HOST='localhost'
PORT=5555

logging.basicConfig(filename="server.log", level=logging.DEBUG)


class Server:
    """Chat Server process."""
    
    def __init__(self):
        self.ssock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.ssock.bind((HOST,PORT))
        self.ssock.listen(10) 
        self.selec=selectors.DefaultSelector()
        
        #canais dictionary
        self.canais={}
        
        self.selec.register(self.ssock,selectors.EVENT_READ,self.accept)
        print("Server is running...")
        
        
        
        
    def accept( self,sock,mask):
        
        conn,addr=sock.accept()
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        self.canais[conn]=[None]
        
        self.selec.register(conn, selectors.EVENT_READ, self.read)
        
    
    def read(self,conn,mask):
        
        
        
        message = CDProto.recv_msg(conn)
        logging.debug('received "%s', message)
            
            
        if message!=None:
            if message.command=="register":
                print(f'{message.user} joined the server!!')
                CDProto.send_msg(conn,message)
                logging.debug('registered "%s',message.user)
                    
            elif message.command=="join":
                if (self.canais[conn]==[None]):
                    self.canais[conn]=[message.channel]
                elif(self.canais[conn]!=[None] and message.channel not in self.canais[conn]):
                    self.canais[conn].append(message.channel)
                else:
                    print("You are already in this channel")
                print(f'User joined the channel {message.channel}')
                logging.debug('"User joined "%s',self.canais[conn])
                    
            elif message.command =="message":
                    for client,canais in self.canais.items():
                        if (message.channel in canais):
                            CDProto.send_msg(client,message)
                            print(f'User sent "{message.message}" to channel {message.channel}')
                            logging.debug('"User sent "%s',message)
                                
        else:
            print(f"Conection closed.") 
            self.selec.unregister(conn)
            self.canais.pop(conn)
            conn.close()

        
    def loop(self):
        """Loop indefinetely."""
        while True: 
            events = self.selec.select()
            for key, mask in events:
                callback = key.data 
                callback(key.fileobj, mask)

