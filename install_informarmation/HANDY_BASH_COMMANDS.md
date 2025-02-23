# Handy bash command listgs

## Can Bus commands 
```bash
ip link set can0 up type can bitrate 50000  # Set up CAN0 with 50 kbps
ip link set can0 down                        # Disable CAN0
ip link show
candump can0                                 # Monitor CAN traffic
candump can0 -l                              # Put can dump in log file
cansend can0 0E094000#001C                   # Send a wake-up CAN message
cansend can0 0E094000#001A                   # Send a sleep CAN message
cansniffer can0                              # Sniff CAN messages in real time
```

## Bluetooth connect
```bash
bluetoothctl                    # Opens bluethooth ctl terminal
```

to connect
```bash
power on
agent on
discoverable on
pairable on
scan on
connect aa:aa:aa:aa:aa         # found mac adres of machine
```

## Logging & debugging
```bash
dmesg | tail -20         # Show last 20 system messages
journalctl -xe           # View system logs
sudo systemctl status bluetooth  # Check Bluetooth service status
sudo systemctl restart bluetooth  # Restart Bluetooth service
sudo systemctl status can0        # Check CAN interface status
```