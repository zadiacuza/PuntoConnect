#!/bin/bash

sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 50000 loopback off
sudo ip link set can0 up
echo "CAN0 enabled"
