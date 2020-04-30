#! /bin/sh

# op25 install script for debian based systems
# including ubuntu 14/16 and raspbian

sudo apt-get update
sudo apt-get build-dep gnuradio
sudo apt-get install gnuradio gnuradio-dev gr-osmosdr librtlsdr-dev libuhd-dev  libhackrf-dev libitpp-dev libpcap-dev cmake git swig build-essential pkg-config doxygen python-numpy

mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig

