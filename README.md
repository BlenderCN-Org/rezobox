# rezobox
Creuser et trouver des réseaux post-neuronaux.


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
#### Blender
~~~text
sudo apt-get install blender
~~~

#### Python
~~~text
sudo apt-get install python-dev python-setuptools
sudo pip install twisted
sudo pip install opencv
sudo pip install numpy

sudo apt-get install python3-dev python3-setuptools
sudo pip3 install opencv
sudo pip3 install numpy
sudo pip3 install twisted
~~~

### Exécution du jeu
#### Kinect
Double clic sur clic_to_run_kinect

#### Blender
Double clic sur clic_to_run_game

### Merci à:

* [Labomedia]( https://labomedia.org/)
