#!/bin/bash
for i in {1..5}; do
    busctl call org.bluez /org/bluez/hci0/dev_08_8B_C8_6D_3E_50 org.bluez.MediaControl1 Pause
    sleep 0.3  # Adjust delay if needed
done