# PuntoConnect scripts
A b&m replacement running on a raspberry pi 4 model b

## for development
For development it is recommended to test withn vcan0 
```bash
python3 devUtils/enable_vcan0.py
```

Also checkout the car dashboard simulator project for testing
it will show a drawing of a punto dashboard and steeringwheel
including the buttons in the car.

When trying to connect to diffrent car make a 30m 
(or what ever you prefere) candump first. with can0 
connected to cars B-BUS
```bash
candump -l
```
And then replay the bus when using the vcan0
```bash
canplayer -I candump-*.log
```

