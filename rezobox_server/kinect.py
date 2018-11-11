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
        self.mini = int(self.conf["image"]["mini"])
        self.maxi = int(self.conf["image"]["maxi"])
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
        except:
            array = self.default_image
            
        array = np.array(array, dtype=np.uint8)
        
        return array

    def get_sandbox(self, depth):
        """
        20 < sandbox  < 95
        sandbox.shape = 480, 640
        """
        mask = cv2.inRange(depth, self.mini, self.maxi)
        img = cv2.bitwise_and(depth, depth, mask=mask)
        
        return img

    def get_detected(self, img):
        detected = change_resolution(img, (self.width, self.height))
        
        return detected

    def get_cropped(self, depth):
        
        y = int(self.conf["crop"]["y"])
        h = int(self.conf["crop"]["h"])

        x = int(self.conf["crop"]["x"])
        w = int(self.conf["crop"]["w"])

        return depth[y:y+h, x:x+w]

        
class Display(object):

    def __init__(self, conf):
        self.loop = 1
        self.kinect = Kinect(conf)
        self.msg = b"toto"
        print("Display initié")

    def one_loop(self):
        #frame = self.kinect.get_RGB_video()
        depth = self.kinect.get_depth()

        cropped = self.kinect.get_cropped(depth)
        sandbox = self.kinect.get_sandbox(cropped)
        detected = self.kinect.get_detected(sandbox)

        self.msg = array_to_bytes(detected)
        
        # #cv2.imshow('RGB image',frame)
        big = change_resolution(detected, (1066, 800))
        cv2.imshow('Kinect', big)
            
        # quit program when 'esc' key is pressed
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            self.loop = 0
            cv2.destroyAllWindows()
            
    def infinite_loop(self):
        while self.loop:
            #frame = self.kinect.get_RGB_video()
            depth = self.kinect.get_depth()

            cropped = self.kinect.get_cropped(depth)
            sandbox = self.kinect.get_sandbox(cropped)
            detected = self.kinect.get_detected(sandbox)
            
            self.msg = array_to_bytes(detected)
            
            big = change_resolution(detected, (1066, 800))

            # Display
            cv2.imshow('Kinect', big)
            
            # quit program when 'esc' key is pressed
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break
                
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
    scr = os.path.dirname(os.path.abspath(__file__))
    cf = MyConfig(scr + "/rezobox_server.ini")
    conf = cf.conf
    print("Configuration du serveur: {}\n".format(conf))
    disp = Display(conf)
    disp.infinite_loop()

    
if __name__ == "__main__":
    main()
