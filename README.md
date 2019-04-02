# Pygame Laberinto
Laberinto hecho con el modulo pygame en python 3, este con opcion para modo one-player y multiplayer, esto
mediante uso de red local
### Descripcion del juego
* El juego permite ingresar como invitado, se trata de jugar de manera individual
* Como multiplayer se puede jugar de manera individual y multijugador, en individual 
guarda el record mas alto en caso
de existir y para multijugador quien tiene mas puntaje al final de la partida
### Modulos usados
```
* Pygame 
* Sockets
* Daemonize
* MongoDB
* threading
* Json
```
### Instalar
```
pip3 install pymongo
pip3 install daemonize
pip3 install -U pygame --user
```
### Ejecutar juego y servidor
El servidor debe estar corriendo en una maquina para entregar todos los datos del 
laberinto, se puede ejecutar en modo normal y modo demonio
```
Modo normal: python3 server.py
Modo demonio: python3 daemon.py
```
Para ejecutar el juego:
```
python3 main.py
```
### Observaciones
* Falta implementar la informacion acerca de los records tanto de manera individual y multijugador
* No hay juego si el servidor no se esta ejecutando