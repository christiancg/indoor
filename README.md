# indoor

Setup del sistema (https://www.pyimagesearch.com/2015/10/26/how-to-install-opencv-3-on-raspbian-jessie/)

## Actualizacion de todo el SO
* sudo apt-get update
* sudo apt-get upgrade
* sudo rpi-update
* sudo reboot now

## Librerias para la app del indoor
* sudo pip install flask_sqlalchemy
* sudo pip install pika

## Herramientas de buildeo
* sudo apt-get install build-essential git cmake pkg-config

## Libreria de imagenes para la camara
* sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev

## Librerias de video para la camara
* sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
* sudo apt-get install libxvidcore-dev libx264-dev

## Librerias de optimizacion de OpenCV
* sudo apt-get install libatlas-base-dev gfortran

## Instalar herramientas de desarrollo de python
* sudo apt-get install python2.7-dev python3-dev

## Instalar GTK por si queremos mostrar cosas en la pantalla
* sudo apt-get install libgtk2.0-dev

## Instalar numpy para opencv
* pip install numpy

## Descarga, configuracion e instalacion de OpenCV
* cd ~/Downloads
* wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.0.0.zip
* unzip opencv.zip
* wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.0.0.zip
* unzip opencv_contrib.zip
* cd opencv-3.0.0/
* mkdir build
* cd build
* cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_EXTRA_MODULES_PATH=~/Downloads/opencv_contrib-3.0.0/modules -D BUILD_EXAMPLES=ON -D BUILD_PYTHON_SUPPORT=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D PYTHON_INCLUDE_DIR=/usr/include/python2.7 -D PYTHON_LIBRARY=/usr/lib/arm-linux-gnueabihf/libpython2.7.so -Wno-dev ..
* make -j4
* sudo make install
* sudo ldconfig

## Instalar PIP para instalar paquetes de Python
* wget https://bootstrap.pypa.io/get-pip.py
* sudo python get-pip.py

## Chequear que sea hayan instalado las librerias de OpenCV
* ls -l /usr/local/lib/python2.7/site-packages/ | grep cv2
