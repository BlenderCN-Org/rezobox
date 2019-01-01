# rezobox
Creuser et trouver des réseaux post-neuronaux.

![ReZobox](/rezobox_rendu_3.jpg)


### Très inspiré de [AR Sandbox](https://arsandbox.ucdavis.edu/)

### Principe

* Capture par une Kinect avec des scripts python2, opencv, twisted.
* Envoi d'une image en niveau de gris de 100x75 pixels en TCP en local.
* Réception dans le Blender Game Engine avec des scripts en python3
* Pour chaque pixel, un plan est ajouté qui masque l'image en dessous. La position verticale du plan est fonction de la capture Kinect.

### Documentation
* [RezObox](https://ressources.labomedia.org/rezobox)

### Version de python

* Le serveur et la Kinect sont en python2
* Les scripts dans le Blender Game Engine sont en python3

### License and Copyright

This game is under Creative Commons Attribution-ShareAlike 3.0 Unported License.

All scripts are under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
More in file License GPL V3.

## Contexte
* Debian Stretch 9.3  avec Blender 2.79
* Novembre 2018

### Installation

~~~text
sudo apt-get install blender git python-dev python-setuptools python-pip python3-pip python-freenect python3-dev python3-setuptools

sudo pip install twisted numpy opencv-python
sudo pip3 install twisted numpy opencv-python
~~~

#### Récupération des sources sur GitHub

~~~text
git clone https://github.com/sergeLabo/rezobox.git
~~~

Mise à jour dans le dossier

~~~text
git pull
~~~

### Exécution du jeu
#### Kinect
Double clic sur clic_to_run_kinect

#### Blender
Double clic sur clic_to_run_game

### Définitions des valeurs dans les fichiers *.ini
#### rezobox_server.ini

**server**

* port = 8888
* ip = "127.0.0.1"
* tempo = 0.8

**image**

* trackbars = avec ou sans trackbars, ne marche pas avec le serveur = 0 ou 1
* thread = pour test dans kinect.py, simule le serveur; 0 ou 1
* x = hauteur de l'image reçue du serveur = 75
* y = largeur de l'image reçue du serveur = 100
* mini = 66 gris mini
* maxi = 80 gris maxi

** Affichage de Fenêtre OpenCv **

* depth = 0 image brute sortie kinect
* cropped = 0 image coupée autour
* mask = 0 mask avec mini maxi
* sandbox = 0 sortie avec le masque appliqué
* detected = 1 ce qui est envoyé à Blender
* big = 0 = detected aggrandi

**crop**

* y = coupe en haut 138
* h = coupe en bas 64
* x = coupe à gauche 89
* w = coupe à droite 156

#### resobox.ini pour Blender

**tcp**

* ip = "127.0.0.1"
* port = 8888

**image**

* y = hauteur de l'image reçue du serveur = 75
* x = largeur de l'image reçue du serveur = 100
* gray = si gris < gray, l'herbe est invisible

**plane**

* life = durée d vie des plans ajoutés = 45 frames
* cycle = Nombre de frames par cycle, 1 pour le réseau, 50 pour l'affichage des plans soit 51
* largeur = largeur des plans carrés ajoutés à chercher dans le layer 2 = 0.110


### Merci à:

* [Labomedia]( https://labomedia.org/)
