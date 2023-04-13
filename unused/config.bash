#!/bin/bash

yum install -y gcc gcc-c++ make automake
yum install -y wget
yum -y install rsync
yum -y install lua
yum -y install
tar -zxvf cmake-3.24.3.tar.gz
cd cmake-2.8.10.2
./bootstrap
gmake
gmake install