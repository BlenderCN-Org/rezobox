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

"""
kinect à 147 cm du fond du bac
"""

import os
from time import time

import freenect
import cv2
import numpy as np

from myconfig import MyConfig


class Kinect(object):

    def __init__(self, conf):
        print("Kinect initialisé")

        self.conf = conf
        
        self.height = int(self.conf["image"]["x"])
        self.width = int(self.conf["image"]["y"])
        
        self.default_image = get_default_image()
        
    def get_RGB_video(self):
        """
        Get RGB image from kinect
        """
        array, integer = freenect.sync_get_video()
        array = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
        return array
 
    def get_depth(self):
        """
        Get depth image from kinect
        """
        try:
            array, integer = freenect.sync_get_depth()
            print('Kinect ok')
        except:
            array = self.default_image
            
        array = np.array(array, dtype=np.uint8)
        
        return array

    def get_sandbox(self, depth, mini, maxi):
        """passe en noir les pixels en dehors de la plage
        20 < sandbox  < 95
        sandbox.shape = 480, 640
        """

        mask = cv2.inRange(depth, mini, maxi)
        img = cv2.bitwise_and(depth, depth, mask=mask)
        
        return img, mask

    def get_detected(self, img):
        """
        Passe à résolution à 100x75
        """
        detected = change_resolution(img, (self.width, self.height))
        
        return detected

    def get_cropped(self, depth, y , h, x, w):
        """
        y = coupe en haut
        h = coupe en bas
            y: 480 - h
        """
        height, width = depth.shape
        
        return depth[y:height-h, x:width-w]

        
class Display(object):

    def __init__(self, my_conf):
        # Object MyConfig
        self.my_conf = my_conf
        # La config est attribut de my_conf
        self.conf = my_conf.conf
        
        self.loop = 1
        self.kinect = Kinect(self.conf)
        self.msg = b"toto"

        self.y = self.conf['crop']['y']
        self.h = self.conf['crop']['h'] 
        self.x = self.conf['crop']['x']
        self.w = self.conf['crop']['w']
        self.mini = int(self.conf["image"]["mini"])
        self.maxi = int(self.conf["image"]["maxi"])
        
        # Initialisation des trackbars
        self.trbr = self.conf['image']['trackbars']
        if self.trbr:
            self.trackbars()
            self.set_init_tackbar_position()
        
        print("Display initié")

    def trackbars(self):
        """ [crop] y = 20 h = 20 x = 20 w = 20 """
        
        cv2.namedWindow('Capture original')
        
        # create trackbars for crop change
        cv2.createTrackbar('y', 'Capture original', 0, 200, self.onChange_y)
        cv2.createTrackbar('h', 'Capture original', 0, 200, self.onChange_h)
        cv2.createTrackbar('x', 'Capture original', 0, 200, self.onChange_x)
        cv2.createTrackbar('w', 'Capture original', 0, 200, self.onChange_w)
        cv2.createTrackbar('mini', 'Capture original',  0, 255, self.onChange_mini)
        cv2.createTrackbar('maxi', 'Capture original',  0, 255, self.onChange_maxi)
        
    def set_init_tackbar_position(self):
        """
        setTrackbarPos(trackbarname, winname, pos) -> None
        """
        cv2.setTrackbarPos('y', 'Capture original', self.y)
        cv2.setTrackbarPos('h', 'Capture original', self.h)
        cv2.setTrackbarPos('x', 'Capture original', self.x)
        cv2.setTrackbarPos('w', 'Capture original', self.w)
        cv2.setTrackbarPos('mini', 'Capture original', self.mini)
        cv2.setTrackbarPos('maxi', 'Capture original', self.maxi)
        
    def onChange_y(self, y):
        """ coupe verticale en haut """
        self.y = y
        self.save_change('crop', 'y', y)

    def onChange_h(self, h):
        """ coupe verticale en bas """
        self.h = h
        self.save_change('crop', 'h', h)

    def onChange_x(self, x):
        """ coupe horizontale à gauche """
        self.x = x
        self.save_change('crop', 'x', x)

    def onChange_w(self, w):
        """ coupe horizontale à droite """
        self.w = w
        self.save_change('crop', 'w', w)

    def onChange_mini(self, mini):
        """ mini à extraire """
        self.mini = mini
        self.save_change('image', 'mini', mini)

    def onChange_maxi(self, maxi):
        """ mini à extraire """
        self.maxi = maxi
        self.save_change('image', 'maxi', maxi)
        
    def save_change(self, section, key, value):
        self.my_conf.save_config(section, key, value)
        
    def one_loop(self):

        depth = self.kinect.get_depth()

        # Affichage capture originale
        cv2.imshow('Capture original', depth)

        # Capture des positions des sliders
        if self.trbr:
            self.y = cv2.getTrackbarPos('y','Capture original')
            self.h = cv2.getTrackbarPos('h','Capture original')
            self.x = cv2.getTrackbarPos('x','Capture original')
            self.w = cv2.getTrackbarPos('w','Capture original')
        
        # Image coupée sur les bords
        cropped = self.kinect.get_cropped(depth, self.y, self.h, self.x, self.w)
        # Affichage de l'image coupée
        cv2.imshow('Capture cropped', cropped)

        # Masque sur gris mini maxi
        sandbox, mask = self.kinect.get_sandbox(cropped, self.mini, self.maxi)
        cv2.imshow('Masque', mask)
        cv2.imshow('Sandbox', sandbox)

        # Résoltution à 100x75, sera envoyé à Blender
        detected = self.kinect.get_detected(sandbox)

        # Message à envoyer à Blender
        self.msg = array_to_bytes(detected)
        
        big = change_resolution(detected, (640, 480))
        cv2.imshow('Kinect finale', big)
        
        # quit program when 'esc' key is pressed
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            self.loop = 0
            cv2.destroyAllWindows()


def get_default_image():
    scr = os.path.dirname(os.path.abspath(__file__))
    img = cv2.imread(scr + "/images/depth_640_480.png", 0)
    print("Default image", img.size, img.shape)
    return img

def change_resolution(img, (x, y)):
    return cv2.resize(img, (x, y), interpolation=cv2.INTER_AREA)

def array_to_bytes(array):
    data = array.tobytes()
    return data
    
def main():
    """conf['image']['trackbars']"""
    
    scr = os.path.dirname(os.path.abspath(__file__))
    my_conf = MyConfig(scr + "/rezobox_server.ini")
    conf = my_conf.conf
    print("Configuration du serveur: {}\n".format(conf))

    disp = Display(my_conf)

    if not conf['image']['thread']:
        print('Test kinect sans thread')
        while 1:
            disp.one_loop()
    else:
        print('Test kinect avec thread')
        kinect_thread(disp)

def kinect_thread(disp):
    import threading
    thread_disp = threading.Thread(target=kinect_loop,args=(disp, ))
    thread_disp.start()
        
def kinect_loop(disp):
    from time import sleep
    while 1:
        sleep(1)
        disp.one_loop()

        
if __name__ == "__main__":
    main()
