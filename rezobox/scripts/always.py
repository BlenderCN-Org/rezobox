#!/usr/bin/env python3
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
Lancé à chaque frame durant tout le jeu.
"""

import sys
from time import time
from math import sin, cos, tan
import random

import numpy as np
import cv2
    
from bge import logic as gl
import scripts.blendergetobject

def droiteAffine(x1, y1, x2, y2):
    """
    Retourne les valeurs de a et b de y=ax+b
    à partir des coordonnées de 2 points.
    """

    a = (y2 - y1) / (x2 - x1)
    b = y1 - (a * x1)
    return a, b

# 0 à 20 => 1.55, 94 => -1.5
A, B = droiteAffine(20, 1.55, 94, -1.48)

def get_server_message():
    t0 = time()
    gl.clt.re_connect_sock()
    try:
        data = gl.clt.listen(16384)
        print("\nMessage reçu: taille =", str(sys.getsizeof(data)))
        # Prends beucoup trop de temps
        #gl.clt.clear_buffer(16384)
    except:
        data = None
        print("Pas de réception sur le client TCP")
    print("    en {0:.2f} seconde".format(time() - t0))
    
    return data

def get_image(data):
    h, w = gl.y, gl.x
    nparray = np.fromstring(data, np.uint8)
    
    print("Taille du array de l'image reçue:", nparray.size)
    print("x =", gl.x, "y =", gl.y, "x*y =", gl.y*gl.x)
    
    if nparray.size == gl.size:
        image = nparray.reshape(h, w)
    else:
        image = gl.image
    return image

def add_object(obj, position, life, all_obj, game_scn):
    """
    Ajoute obj à la place de Empty
    position liste de 3
    
    addObject(object, reference, time=0)
    Adds an object to the scene like the Add Object Actuator would.
    Parameters:	
        object (KX_GameObject or string) – The (name of the) object to add.
        reference (KX_GameObject or string) – The (name of the) object which
        position, orientation, and scale to copy (optional), if the object
        to add is a light and there is not reference the light’s layer will be
        the same that the active layer in the blender scene.
        time (integer) – The lifetime of the added object, in frames. A time
        of 0 means the object will last forever (optional).

    Returns: The newly added object.
    Return type: KX_GameObject
    """
    empty = all_obj['Empty']
    empty.worldPosition = position
    
    return game_scn.addObject(obj, empty, life)
    
def add_one_row_planes(image, row, all_obj, game_scn):
    """
        Ajout les plans d'une image de 1 colonne en position x = row
        largeur du box = 11
        un plan = 11/100 = 0,110

    """
    
    # plan de coté = pas de 11/100 = 0,110
    lp = gl.largeur_plan
    
    for h in range(gl.y):
        # longueur du box: 100 * 0.110 = 11.0
        # largeur  du box:  75 * 0.110 = 8.25

        # row de 0 à 63 ( row pas + demi pas - demi longueur de box )
        x = row*lp + lp/2 - 5.5

        # -( h pas + demi pas - demi largeur de box )
        y = - (h*lp + lp/2 - 4.125)
                
        # image[h][0] de 0 à 94
        p = image[h][0]


        a, b = -0.04094, 2.3689
        z = a * p + b
        if z > 1.48:
            z = 1.48
                
        # Ajout
        add_object("Plane", (x, y, z), gl.life, all_obj, game_scn)

def add_planes(all_obj, game_scn):
    """ Ajout des plans par 2 colonnes
    """
    # nombre de colonne par frame = 2
    ncpf = 2
    
    # Compte de 0 à 50 compris, 51 repasse à 0
    cycle = gl.tempoDict["cycle"].tempo
    
    # cycle = 0 récup réseau, puis de 1 à 50 et row de 0 à 99
    for row in range(1, 100, 2):
        # row = 98 0 2 4 6 .... 96 98 0 2 
        # tempo = 0 1 2 ........50
        row -= 1
        if 2*cycle == row and gl.image is not None:
            
            # Tranche verticale d'image de 1 colonne
            image_parts = gl.image[0:gl.y, row:row+1]
            # ajout de la colonne
            add_one_row_planes(image_parts, row, all_obj, game_scn)
            
            # Tranche verticale d'image de 1 colonne
            image_parts = gl.image[0:gl.y, row+1:row+2]
            # ajout de la colonne
            add_one_row_planes(image_parts, row+1, all_obj, game_scn)

def hide_herbe_good(all_obj):
    """Division d'un plan texturé:
    https://blender.stackexchange.com/questions/1437/subdivide-and-separate-face-into-different-meshes

    In Edit mode -> Select the face
    W -> Subdivde -> tool shelf T or F6 -> Number of Cuts (in your case 3)
    With the subdivided faces selected -> Ctrl + E -> mark sharp
    Add edge split modifier -> uncheck edge angle
    In Object mode apply the edge split modifier
    (optional) in Edit mode -> select the faces if not selected -> Ctrl + E -> clear sharp
    In Edit mode -> P -> separate by loose parts (séparer par partie mal fixée, pas attachées)

    objet herbe = coordonnées X, Y
    """
    if gl.image is not None:
        n = 40
        # Diminution de la résolution de l'image
        img = cv2.resize(gl.image, (n, n), interpolation=cv2.INTER_AREA)
        # Mirror sur x: 0 = h, 1 = v, -1 = both
        img = cv2.flip(img, 0)

        gray_list = []
        points_list = []
        gray_ref = gl.conf["image"]["gray"]
        # Parcours des objets "herbe"
        for obj in all_obj:
            if "herbe" in obj:
                x_herbes, y_herbes = get_position(all_obj[obj])

                # box = 11, 8.25
                # x_herbes de -5.5 à + 5.5
                # largeur 11 de blender = 40 pixels
                # de 0 à 43, il faut 0 à 39 inclus
                x = int(4 * (x_herbes + 5.5) * 39 / 43)

                # hauteur 8.25 de blenbder = 40 pixels
                # de 0 à 30, il faut 0 à 39 inclus
                y = int(4 * (y_herbes + 4.125) * 36 / 30)
                
                points_list.append(x)
                
                gray = img[y][x]
                gray_list.append(gray)
                
                if gray >= gray_ref:
                    all_obj[obj].visible = False
                else:
                    all_obj[obj].visible = True
                    
def hide_herbe_simple(all_obj):
    """Cache tout"""
    for obj in all_obj:
        if "herbe" in obj:
            all_obj[obj].visible = False

def get_position(plan):
    """Le centre de l'objet est 0,0,0
    je calcule la position d e la moyenne des 4 vertices du plan
    """
    # Liste de 4 liste de 3
    vl = get_plane_vertices_position(plan)

    # Moyenne des x
    x = (vl[0][0] + vl[2][0])/2
    # Moyenne des y
    y = (vl[0][1] + vl[1][1])/2
        
    return x, y

def get_plane_vertices_position(obj):
    """Retourne les coordonnées des vertices d'un plan
    [[5.5, -4.125, 1.5], [5.5, -3.375, 1.5], [4.5, -3.375, 1.5],
                                                    [4.5, -4.125, 1.5]]
    """
    verts = []
    a = 0
    for mesh in obj.meshes:
        a += 1
        for m_index in range(len(mesh.materials)):
            for v_index in range(mesh.getVertexArrayLength(m_index)):
                verts.append(mesh.getVertex(m_index, v_index))

    vertices_list = []
    for i in range(4):
        vertices_list.append([verts[i].x, verts[i].y, verts[i].z])

    return vertices_list

def draw_line(all_obj, game_scn):
    x = gl.x_line
    y = gl.y_line
    z = gl.z_line
     
    x += 0.08 * 2
    if x > 5.5:
        x = -5.5
        
    y = sin(x)/2
    # pour faire descendre la sinusoide
    # #y += x/5 
    
    z = 1.43
    
    position = x, y, z
    life = 30
    obj = "ligne pixel"

    # Ajout de l'objet
    pixel = add_object(obj, position, life, all_obj, game_scn)

    # Modification de l'objet ajouté
    pixel.worldOrientation = 0, 0, 0.5 * cos(x)
    pixel.localScale = 1.45, 1, 1

    # Save values
    gl.x_line = x
    gl.y_line = y
    gl.z_line = z    

def get_gray_average():
    # Valeur moyenne du gris
    try:
        moy = np.mean(gl.image)
        print("Moyenne du gris =", moy)
        return moy
    except:
        return 0

def sound():
    """
        gl.sound["rose"].set_pitch(pitch)

    try:
        gl.sound["rose"].set_pitch(pitch)
        gl.sound["rose"].play()
    except:
        print("ereur")
    """
    average = get_gray_average()
    
    try:
        pitch = 1 + 110/average
    except:
        pitch = 1

    factory = aud.Factory.sine(440*pitch)
    
    # play the audio, this return a handle to control play/pause
    gl.handle = gl.device.play(factory)

def sound_stop():
    try:
        gl.handle.stop()
    except:
        print("Pas de son en cours")
  
def sound_rose():
    """gl.handle_rose =
    ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'attenuation', 'cone_angle_inner', 'cone_angle_outer', 'cone_volume_outer', 'distance_maximum', 'distance_reference', 'keep', 'location', 'loop_count', 'orientation', 'pause', 'pitch', 'position', 'relative', 'resume', 'status', 'stop', 'velocity', 'volume', 'volume_maximum', 'volume_minimum']
    
    gl.factory = 
    ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'buffer', 'delay', 'fadein', 'fadeout', 'file', 'filter', 'highpass', 'join', 'limit', 'loop', 'lowpass', 'mix', 'pingpong', 'pitch', 'reverse', 'sine', 'square', 'volume']

    gl.factory.pitch = <built-in method pitch of aud.Factory object at 0x7f0b806fddd0>
    
    random.choice([1, 2, 3, 4, 5])
    """
    # ne change pas le pitch mais la durée
    gl.factory.pitch(10.0)
    gl.handle_rose = gl.device.play(gl.factory)

def sound_rose_stop():
    try:
        gl.handle_rose.stop()
    except:
        print("Pas de son en cours")
           
def main():
    """
    frame 0 update réseau
    frame 1 à 51 affichage des 25*2 rows
    """
    # Update des tempo
    gl.tempoDict.update()

    if gl.tempoDict["cycle"].tempo == 0:
        # calcul du FPS
        t = time()
        print("\n     Début d'un cycle")
        print("Durée d' un cycle = {0:.2f} seconde".format(t - gl.tzero))
        print("    soit un FPS de {0:.0f}".format(51/(t - gl.tzero)))
        gl.tzero = t
    
        data = get_server_message()
        
        if data:
            gl.image = get_image(data)

        # du son
        sound_rose()

    #draw_line(all_obj, game_scn)
    
    all_obj = scripts.blendergetobject.get_all_objects()
    game_scn = scripts.blendergetobject.get_scene_with_name('Labomedia')
            
    # Ajout des plans pour cycle de 1 à 50 compris
    add_planes(all_obj, game_scn)

    # Effacement de l'herbe
    if gl.tempoDict["cycle"].tempo == 0:
        all_obj = scripts.blendergetobject.get_all_objects()
        hide_herbe_good(all_obj)

    # Stop son
    if gl.tempoDict["cycle"].tempo == 51:
        print("Stop du son")     
        sound_rose_stop()
