#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
# This file is part of rezobox.
#
# rezobox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rezobox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
########################################################################


import os, sys
from time import sleep
import threading

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

from myconfig import MyConfig
from kinect import Display

# Variable globale
scr = os.path.dirname(os.path.abspath(__file__))

# L'object configuration
conf_obj = MyConfig(scr + "/rezobox_server.ini")
CONF = conf_obj.conf
print("Configuration du serveur: {}\n".format(CONF))

TCP_PORT = CONF["server"]["port"]
TEMPO = float(CONF["server"]["tempo"])
TO_BLEND = None


class MyTcpServer(Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.loop = 1
        
    def connectionMade(self):
        self.addr = self.transport.client
        print("self.transport", self.transport)
        print("Une connexion établie par le client {}".format(self.addr))
        self.sender_thread()
        
    def connectionLost(self, reason):
        print("Connection lost, reason:", reason)
        print("Connexion fermée avec le client {}".format(self.addr))
        self.loop = 0

    def sender(self):
        global TO_BLEND
        
        while self.loop:
            sleep(TEMPO)
            try:
                data = TO_BLEND
                print("Server: Message envoyé avec taille =", str(sys.getsizeof(data)))
            except:
                data = None

            if data:
                try:
                    self.transport.write(data)
                except OSError as e:
                    if e.errno == 101:
                        print("Network is unreachable")
                    
    def sender_thread(self):
        print("Envoi au client", self.transport)
        thread_send = threading.Thread(target=self.sender)
        thread_send.start()
          
    def dataReceived(self, data):
        print("Server: Message reçu =", data)
        
    
class MyTcpServerFactory(Factory):
    """
    Le self d'ici sera self.factory dans les objets MyTcpServer.
    """
    global TO_BLEND, CONF

    def __init__(self):
        global CONF
        self.loop = 1

        self.display = Display(conf_obj)

        self.kinect_thread()
    
        # Suivi des clients
        self.numProtocols = 1
        
        # Serveur
        print("Serveur twisted réception TCP sur {}\n".format(TCP_PORT))

    def buildProtocol(self, addr):
        print("Nouveau protocol crée dans l'usine: factory")
        print("Nombre de protocol dans factory", self.numProtocols)

        # le self permet l'accès à self.factory dans MyTcpServer
        return MyTcpServer(self)

    def kinect_loop(self):
        global TO_BLEND
        while self.loop:
            print TEMPO
            sleep(TEMPO)
            self.display.one_loop()
            TO_BLEND = self.display.msg
            
    def kinect_thread(self):
        thread_disp = threading.Thread(target=self.kinect_loop)
        thread_disp.start()

    
if __name__ == "__main__":
    # Server TCP
    endpoint = TCP4ServerEndpoint(reactor, TCP_PORT)
    endpoint.listen(MyTcpServerFactory())

    reactor.run()
