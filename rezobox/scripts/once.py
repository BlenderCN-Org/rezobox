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
Ce script est appelé par main_init.main dans blender
Il ne tourne qu'une seule fois pour initier lss variables
qui seront toutes des attributs du bge.logic (gl)
Seuls les attributs de logic sont stockés en permanence.
"""

from time import time
from bge import logic as gl
import aud

from scripts.myconfig import MyConfig
from scripts.tcpclient3 import TcpClient3
from scripts.blendertempo import Tempo
from scripts.blendersound import EasyAudio

def get_conf():
    """Récupère la configuration depuis le fichier *.ini."""

    # Le dossier courrant est le dossier dans lequel est le *.blend
    current_dir = gl.expandPath("//")
    print("Dossier courant depuis once.py {}".format(current_dir))
    gl.once = 0

    # TODO: trouver le *.ini en auto
    gl.ma_conf = MyConfig(current_dir + "scripts/rezobox.ini")
    gl.conf = gl.ma_conf.conf

    print("\nConfiguration du jeu rezobox:")
    print(gl.conf, "\n")

def create_tcp_client():
    ip = gl.conf["tcp"]["ip"]
    port = int(gl.conf["tcp"]["port"])

    gl.clt = TcpClient3(ip, port)
    print("Client TCP créé")

def variable_init():
    gl.x = int(gl.conf["image"]["x"])
    gl.y = int(gl.conf["image"]["y"])
    gl.size = gl.x * gl.y
    gl.image = None
    gl.life = int(gl.conf["plane"]["life"])
    gl.largeur_plan = float(gl.conf["plane"]["largeur"])
    gl.tzero = time()
    # Clé = tuple(x, y), valeur = z
    gl.plane_dict = {}

def line():
    gl.x_line = 0
    gl.y_line = 0
    gl.z_line = 0
    
def tempo():
    gl.cycle = int(gl.conf["plane"]["cycle"])
    tempo_liste = [("cycle", gl.cycle)]
    gl.tempoDict = Tempo(tempo_liste)

def sound_rose():

    gl.device = aud.device()
    
    # load sound file (it can be a video file with audio)
    gl.factory = aud.Factory('/media/data/3D/projets/rezobox/rezobox/sound/rose.ogg')

def main():
    """Lancé une seule fois à la 1ère frame au début du jeu par main_once."""

    print("Initialisation des scripts lancée un seule fois au début du jeu.")

    # Récupération de la configuration
    get_conf()
    
    create_tcp_client()
    
    variable_init()
    tempo()
    line()
    sound_rose()
    
    # Pour les mondoshawan
    print("ok once.py")
