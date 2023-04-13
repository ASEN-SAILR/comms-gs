#!/bin/bash

# Update Raspberry Pi
sudo apt-get update
sudo apt-get upgrade

# Install dependencies
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libxvidcore-dev libx264-dev
sudo apt-get install libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev libgtk-3-dev
sudo apt-get install libatlas-base-dev gfortran
sudo apt-get install python3-dev python3-pip

# Download OpenCV
cd ~
wget -O opencv.zip https://github.com/opencv/opencv/archive/master.zip
unzip opencv.zip

# Build and install OpenCV
cd opencv-master
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D INSTALL_PYTHON_EXAMPLES=ON \
      -D BUILD_opencv_python3=ON \
      -D ENABLE_NEON=ON \
      -D ENABLE_VFPV3=ON \
      -D WITH_TBB=ON \
      -D WITH_OPENCL=ON \
      -D WITH_OPENMP=ON \
      -D WITH_FFMPEG=ON \
      -D OPENCV_ENABLE_NONFREE=ON \
      -D BUILD_EXAMPLES=ON ..
make -j4
sudo make install
sudo ldconfig
