# PuntoConnect infotainment system 
a replacement for the Blue&Me module in my fiat punto twinair turbo. 

## Hardware
For connecting a raspberry pi to the can B-BUS and using the car for power. I have used the following Hardware:
- Raspberry pi 4 model b 
- Waveshare rs485 can-hat
- 12v -> 5v power converter
- Jack cable
- Old USB (to connect cars USB port to pi)

## Hardware setup and test
setting up the CAN hat and the bluetooth a2p
first lets install all needed libraries.
.

### Step 1: Update Your System**

Ensuring the system is up-to-date:

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install PipeWire and WirePlumber**

Raspberry Pi OS Bookworm includes PipeWire by default. However, to ensure all necessary components are installed, execute:

```bash
sudo apt install -y pipewire pipewire-audio pipewire-pulse wireplumber libspa-0.2-bluetooth bluez
```

### step 3: Enable and Start Services**

Activate the required services:

```bash
systemctl --user enable --now pipewire pipewire-pulse wireplumber
```
```bash
sudo systemctl enable --now bluetooth
```

### Step 4 audio functions settup
To allow your Raspberry Pi to function as a Bluetooth audio sink:

#### Create a Bluetooth Agent Script:
   This script will manage pairing requests automatically.

   ```bash
   sudo nano /usr/local/bin/bt-agent
   ```

   Insert the following content:

   ```python
   #!/usr/bin/python3
   import dbus
   import dbus.service
   import dbus.mainloop.glib
   from gi.repository import GLib

   BUS_NAME = 'org.bluez'
   AGENT_INTERFACE = 'org.bluez.Agent1'
   AGENT_PATH = "/test/agent"

   class Rejected(dbus.DBusException):
       _dbus_error_name = "org.bluez.Error.Rejected"

   class Agent(dbus.service.Object):
       @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
       def Release(self):
           pass

       @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
       def AuthorizeService(self, device, uuid):
           return

       @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
       def RequestPinCode(self, device):
           return "0000"

       @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
       def RequestPasskey(self, device):
           return dbus.UInt32(0)

       @dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
       def DisplayPasskey(self, device, passkey, entered):
           pass

       @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
       def RequestConfirmation(self, device, passkey):
           return

       @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
       def RequestAuthorization(self, device):
           return

       @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
       def Cancel(self):
           pass

   def main():
       dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
       bus = dbus.SystemBus()
       agent = Agent(bus, AGENT_PATH)
       obj = bus.get_object(BUS_NAME, "/org/bluez")
       manager = dbus.Interface(obj, "org.bluez.AgentManager1")
       manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
       manager.RequestDefaultAgent(AGENT_PATH)
       adapter = dbus.Interface(bus.get_object(BUS_NAME, "/org/bluez/hci0"), "org.freedesktop.DBus.Properties")
       adapter.Set("org.bluez.Adapter1", "DiscoverableTimeout", dbus.UInt32(0))
       adapter.Set("org.bluez.Adapter1", "Discoverable", True)
       GLib.MainLoop().run()

   if __name__ == "__main__":
       main()
   ```

   Save and exit the editor.

#### Make the Script Executable:**

   ```bash
   sudo chmod +x /usr/local/bin/bt-agent
   ```

3. Create a Systemd Service for the Bluetooth Agent:**

   ```bash
   sudo nano /etc/systemd/system/bt-agent.service
   ```

   Add the following content:

   ```ini
   [Unit]
   Description=Bluetooth Agent
   After=bluetooth.service
   PartOf=bluetooth.service

   [Service]
   ExecStart=/usr/local/bin/bt-agent
   Type=simple

   [Install]
   WantedBy=bluetooth.target
   ```

   Save and exit the editor.

#### 4. Enable and Start the Bluetooth Agent Service:**

   ```bash
   sudo systemctl enable --now bt-agent
   ```

**Step 5: Pair and Connect Your Bluetooth Device**

1. **Put Your Bluetooth Device in Pairing Mode.**

2. **On the Raspberry Pi, Use `bluetoothctl` to Pair:**

   ```bash
   bluetoothctl
   ```

   In the interactive prompt:

   ```bash
   agent on
   default-agent
   scan on
   ```

   Wait until you see your device's MAC address (e.g., `XX:XX:XX:XX:XX:XX`), then:

   ```bash
   pair XX:XX:XX:XX:XX:XX
   trust XX:XX:XX:XX:XX:XX
   connect XX:XX:XX:XX:XX:XX
   ```

   Replace `XX:XX:XX:XX:XX:XX` with your device's MAC address.

3. **Exit `bluetoothctl`:**

   ```bash
   exit
   ```

**Step 6: Verify Audio Output**

Once connected, play audio from your Bluetooth device. The sound should output through the Raspberry Pi's audio interface (HDMI, 3.5mm jack, or USB DAC, depending on your setup).

**Optional: Configure Default Audio Sink**

If you have multiple audio outputs and want to set a default:

1. **List Available Sinks:**

   ```bash
   pactl list short sinks
   ```

2. **Set the Default Sink:**

   ```bash
   pactl set-default-sink [SINK_NAME]
   ```

   Replace `[SINK_NAME]` with the name of your desired audio sink.
