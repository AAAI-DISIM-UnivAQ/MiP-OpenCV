# MiP-OpenCV
Wowwee MiP robot avoids red obstacles using OpenCV (real time computer vision) library on a Raspberry Pi 3 with PiCamera module.

<br><h1> Start_env.py </h1>

*Run this file* (on a Raspberry Pi with a PiCamera) *at the beginning or when the enviroment changes*.
<br><br>Allow to take the picture of the start environment using the PiCamera.

<h1> motion-detector.py </h1>

*The main program to be run on the Raspberry Pi.*
<br><br> This program takes a video of the environment and relieves the movements of the Robot (using OpenCV). If the Mip is going to hit a red obstacle, 
it warns the Brain (writing on Redis). In this way the Mip Robot can make an intelligent choice in order to avoid the obstacle.

<h1> robotControlMain.py </h1> 

*The main loop that simulates the Mip-Brain.*
<br><br> The loop consists of three steps (contained in the __init__.py file: **sense**,**think** and **act**).
<br><br> *Sense* : the Brain reads from Redis in order to know if the Mip is going to hit a red obstacle. 
<br> *Think* : once know the situation, the Brain *thinks* and make a choice in order to avoid the obstacles.
<br> *Act* : act the decision and avoid the red obstacle.

<h1> __init__.py </h1>

*Contains the GattTool and Mip classes.*
<br>
<br> 1. GattTool class:
<br> This class provides methods to command the Mip Robot through BLE protocol.
<br>
<br> 2. Mip class: 
<br> This class provides methods of the Mip-Brain. 



