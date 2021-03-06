#!/usr/bin/python
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


import socket
from time import sleep

class TcpClient2:
    """
    Envoi et réception sur le même socket en TCP.
    """

    def __init__(self, ip, port):

        self.ip = ip
        self.port = port
        self.server_address = (ip, port)
        self.data = None
        self.sock = None
        self.connected = 0
        self.create_socket()
        
    def create_socket(self):
        """
        Création du socket sans try, et avec connexion.
        """
        # Création
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(0.05)
            print("    Création du socket client {}".format(self.server_address))

        # Reconnexion toutes les secondes
        # La différence entre python 2 et 3 est là !!!!!!!!!!!!!!!!!!!!!!!!!!!!
        while not self.connected:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect_sock()

    def connect_sock(self):
        sleep(1)
        try:
            self.sock.connect(self.server_address)
            self.connected = 1
            print("Connexion du client sur {}".format(self.server_address))
        except:
            self.connected = 0
            self.sock.close()
            print("Connexion impossible du client sur {}".format(self.server_address))

    def re_connect_sock(self):
        try:
            self.sock.send(bytes('hello'))
        except socket.error as e:
            self.connected = 0
            self.sock.close()
            print("Déconnecté", e)
            self.create_socket()
                
    def send(self, msg):
        """
        Envoi d'un message, avec send, msg doit être encodé avant.
        """

        # Création d'un socket si besoin
        if not self.sock:
            self.create_socket()

        # Envoi
        try:
            self.sock.send(msg)
        except:
            print("Envoi raté: {}".format(msg))
            # Nouvelle création d'une socket
            self.sock.close()
            self.sock = None

    def reconnect(self):
        """
        Reconnexion.
        """

        self.sock = None
        self.create_socket()

    def close_sock(self):
        """
        Fermeture de la socket.
        """

        try:
            self.sock.close()
        except:
            print("La socket client est déjà close")

        self.sock = None

    def listen(self, buff):
        """
        Retourne les data brutes reçues, et vide le buffer TCP
        """

        raw_data = None
        raw_data = self.sock.recv(buff)
        
        return raw_data

    def clear_buffer(self, buff):
        try:
            while self.sock.recv(buff):
                print("Vidange du buffer")
        except:
            print("Buffer vide")
        

if __name__ == "__main__":

    # Test pour kinect
    import numpy as np
    import cv2

    ip = "127.0.0.1"
    port = 8888
    
    h, w = 48, 64
    
    clt = TcpClient2(ip, port)

    while 1:
        clt.re_connect_sock()
        try:
            data = clt.listen(8192)
        except:
            data = None
            print("Pas de réception sur le client TCP")
            
        if data:
            image = np.fromstring(data, np.uint8).reshape( h, w)
            cv2.imwrite("/media/data/3D/projets/rezobox/rezobox_server/test.jpg", image)
            print("test.jpg enregistré")
            
    clt.close_sock()
