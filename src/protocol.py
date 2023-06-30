"""Protocol for chat server - Computação Distribuida Assignment 1."""
import json
from datetime import datetime
from socket import socket
import time


class Message:
    """Message Type."""
    def __init__(self,command):
        self.command =command                               #comando
    
    def __str__(self):
        return f'{{"command": "{self.command}"}}'               #retorna o comando

    
class JoinMessage(Message):
    """Message to join a chat channel."""
    def __init__(self, command,channel):
        super().__init__(command)                   
        self.channel=channel                                #canal
        
    def __str__(self):
        return f'{{"command": "{self.command}", "channel": "{self.channel}"}}'           #retorna o comando e o canal


class RegisterMessage(Message):
    """Message to register username in the server."""
    def __init__(self, command,user):
        super().__init__(command)
        self.user=user                                                     #usuario
        
    def __str__(self):
        return f'{{"command": "{self.command}", "user": "{self.user}"}}'               #retorna o comando e o usuario                                    

    
class TextMessage(Message):
    """Message to chat with other clients."""
    def __init__(self, command,message,channel,ts):
        super().__init__(command)
        self.message=message                                                #mensagem   
        self.channel=channel                                            #canal                              
        self.ts=ts
        
    def __str__(self):
        if self.channel!=None:
            return f'{{"command": "{self.command}", "message": "{self.message}", "channel": "{self.channel}", "ts": {self.ts}}}' 
        else:
            return f'{{"command": "{self.command}", "message": "{self.message}", "ts": {self.ts}}}'
            


class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, username: str) -> RegisterMessage:
        """Creates a RegisterMessage object."""
        return RegisterMessage("register",username)
        

    @classmethod
    def join(cls, channel: str) -> JoinMessage: 
        """Creates a JoinMessage object."""
        return JoinMessage("join",channel)

    @classmethod
    def message(cls, message: str, channel: str = None) -> TextMessage:
        """Creates a TextMessage object."""
        return TextMessage("message",message,channel,int(time.mktime((datetime.now()).timetuple()) + (datetime.now()).microsecond/1e6))

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
        """Sends through a connection a Message object."""
        if type(msg) is RegisterMessage:
            jm = json.dumps({"command" : msg.command, "user" : msg.user}).encode("utf-8")
        
        elif type(msg) is JoinMessage:
            jm = json.dumps({"command" : msg.command, "channel" : msg.channel}).encode("utf-8")
        
        elif type(msg) is TextMessage:
            if(msg.channel==None):
                jm = json.dumps({"command" : msg.command, "message" : msg.message, "ts" : msg.ts}).encode("utf-8")
            else:
                jm = json.dumps({"command" : msg.command, "message" : msg.message, "channel" : msg.channel, "ts" : msg.ts}).encode("utf-8")


        header = len(jm).to_bytes(2, "big")
        
        connection.sendall(header + jm)

    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""
        data= connection.recv(2)
        if data is None:
            return  None
        
        data=int.from_bytes(data,"big")
        message=connection.recv(data).decode("utf-8")
        
        if message!="":
            
            try:
                message=json.loads(message)
                
            except json.decoder.JSONDecodeError:
                raise CDProtoBadFormat
        
            if message["command"]=="register":
                return CDProto.register(message["user"])
            
            elif message["command"]=="join":
                return CDProto.join(message["channel"])
            
            elif message["command"]=="message":
                if "channel" in message:
                    return CDProto.message(message["message"],message["channel"])
                else:
                    return CDProto.message(message["message"])
        
        
        
            


class CDProtoBadFormat(Exception):
    """Exception when source message is not CDProto."""

    def __init__(self, original_msg: bytes=None) :
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")