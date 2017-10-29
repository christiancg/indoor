# indoor

Setup del sistema

## Actualizacion de todo el SO
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo rpi-update

## Herramientas de buildeo
$ sudo apt-get install build-essential cmake pkg-config

## Libreria de imagenes para la camara
$ sudo apt-get install libjpeg8-dev libtiff4-dev libjasper-dev libpng12-dev

## Librerias de video para la camara
$ sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev

## Librerias de optimizacion de OpenCV
$ sudo apt-get install libatlas-base-dev gfortran

## Instalar PIP para paquetes de python
$ wget https://bootstrap.pypa.io/get-pip.py
$ sudo python get-pip.py

## Instalar y configurarar virtualenv
$ sudo pip install virtualenv virtualenvwrapper
$ sudo rm -rf ~/.cache/pip
$ export WORKON_HOME=$HOME/.virtualenvs
$ source /usr/local/bin/virtualenvwrapper.sh
$ source ~/.profile
$ mkvirtualenv cv

## Instalar herramientas de desarrollo de python
$ sudo apt-get install python2.7-dev

## Instalar numpy para opencv
$ pip install numpy

## Descarga, configuracion e instalacion de OpenCV
$ wget -O opencv-2.4.10.zip http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.10/opencv-2.4.10.zip/download
$ unzip opencv-2.4.10.zip
$ cd opencv-2.4.10
$ mkdir build
$ cd build
$ cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON  -D BUILD_EXAMPLES=ON ..
$ make
$ sudo make install
$ sudo ldconfig

## Linkeo de virtualenv a OpenCV
$ cd ~/.virtualenvs/cv/lib/python2.7/site-packages/
$ ln -s /usr/local/lib/python2.7/site-packages/cv2.so cv2.so
$ ln -s /usr/local/lib/python2.7/site-packages/cv.py cv.py
