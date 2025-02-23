# Switching can interfaces

For this branch of the project to work together with the simulator found in diffrent project, we need to switch to vcan0

## 1. Bring down can0 (disable it)

First we start by tuning off the can0 if it is not off already

```bash
sudo ip link set can0 down
```

## 2. Enable the Virtual CAN Interface (vcan0)
If you haven't already loaded the vcan module, do so with:

```bash
sudo modprobe vcan
```

Now, create the vcan0 interface:
```bash
sudo ip link add dev vcan0 type vcan
```

Finally, bring vcan0 up:
```bash
sudo ip link set vcan0 up
```

check if vcan0 is online
```bash
ip link show type vcan
```

