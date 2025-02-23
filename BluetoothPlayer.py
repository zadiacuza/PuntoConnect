import dbus
import dbus.mainloop.glib
import re
import time
from concurrent.futures.thread import ThreadPoolExecutor
from gi.repository import GLib
from ExceptionAwareThread import ExceptionAwareThread


class BluetoothPlayer:

    listeners = {}
    mainloop = None
    bus = None
    connect_thread = None
    should_run = True
    play_status_executor = None
    player_executor = None
    tm = None

    bt_connected = False
    media_connected = False
    music_playing = False
    possible_pause = False
    media_player = None
    now_playing = None

    pause_music = None
    play_music = None
    next_music = None
    prev_music = None

    def __init__(self, tm):
        self.tm = tm
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mainloop = GLib.MainLoop()
        self.bus = dbus.SystemBus()

        self.bus.add_signal_receiver(self.properties_changed,
                                     bus_name="org.bluez",
                                     dbus_interface="org.freedesktop.DBus.Properties",
                                     signal_name="PropertiesChanged",
                                     path_keyword="path")

        self.play_status_executor = ThreadPoolExecutor(max_workers=1)
        self.player_executor = ThreadPoolExecutor(max_workers=4)
        dbus_thread = ExceptionAwareThread(target=self.start)
        dbus_thread.start()

    def start(self):
        self.connect_thread = ExceptionAwareThread(target=self.connect_device)
        self.connect_thread.start()
        self.mainloop.run()

    def evaluate_play_status(self, new_status):
        if new_status == "playing":
            self.possible_pause = False
            self.music_playing = True
            print("[player] music is playing")
            self.fire_event('playing', self.music_playing)
        else:
            self.possible_pause = True
            time.sleep(0.5)
            if self.possible_pause:
                self.music_playing = False
                print("[player] music is paused")
                self.fire_event('playing', self.music_playing)

    def shutdown(self):
        self.should_run = False
        self.mainloop.quit()

    def connect_device(self, mac_address=None):
            retry_count = 0
            max_retries = 2 if mac_address else 3  # Fewer retries if connecting to a specific MAC

            while self.should_run and retry_count < max_retries:
                if not self.bt_connected:
                    print(f"[player] Attempt {retry_count + 1} to connect...")
                    obj = self.bus.get_object("org.bluez", "/")
                    interface = dbus.Interface(obj, "org.freedesktop.DBus.ObjectManager")
                    regexp = re.compile(r"(^/org/bluez/hci[0-9]/dev_([A-F0-9_]+)$)", re.IGNORECASE)

                    for object_path in interface.GetManagedObjects():
                        matches = regexp.match(object_path)
                        if matches:
                            found_mac = matches[2].replace("_", ":").lower()  # Convert to standard MAC format
                            
                            if mac_address and mac_address.lower() != found_mac:
                                continue  # Skip if looking for a specific MAC and it doesn't match

                            print(f"[player] Found device: {found_mac} at {matches[0]}")
                            hciobj = self.bus.get_object("org.bluez", matches[0])
                            hciiface = dbus.Interface(hciobj, "org.bluez.Device1")

                            try:
                                print(f"[player] Connecting to {found_mac}...")
                                hciiface.Connect()
                                self.bt_connected = True
                                print("[player] Connected successfully!")
                                return True  # ✅ Success
                            except dbus.DBusException as e:
                                print(f"[error] Connection to {found_mac} failed: {e}")
                                pass  # Continue trying other devices

                retry_count += 1
                time.sleep(10)  # Wait before retrying

            print("[player] Reached maximum retry limit, stopping connection attempts.")
            return False  # ❌ Failed after max retries

    def properties_changed(self, interface, changed, invalidated, path):
        if interface == "org.bluez.Device1":
            if "Connected" in changed:
                self.bt_connected = changed["Connected"]
                print("[player] connection state: {}".format(self.bt_connected))

        if interface == "org.bluez.MediaControl1":
            if "Player" in changed:
                self.media_player = changed["Player"]
                print("[player] bluetooth media player: " + self.media_player)
                self.connect_player()
            if "Connected" in changed:
                self.media_connected = changed["Connected"]
                if self.media_connected:
                    print("[player] bluetooth media player connected")
                    self.connect_player()
                else:
                    print("[player] bluetooth media player disconnected")
                    self.evaluate_play_status("disconnected")

        elif interface == "org.bluez.MediaPlayer1":
            if "Track" in changed:
                track = changed["Track"]
                if track["Title"] == 'Not Provided':
                    print("Invalid track received:")
                    print(track)
                else:
                    print("[player] track: {} - {}".format(track["Title"], track["Artist"]))
                    self.now_playing = [track["Title"], track["Artist"]]
                    self.tm.send_music(track["Title"], track["Artist"])
                    self.player_executor.submit(self.resend_track)

            if "Status" in changed:
                self.play_status_executor.submit(self.evaluate_play_status, changed["Status"])

            if "Position" in changed:
                player_position = int(changed["Position"]/1000)
                self.fire_event('position', player_position)

    def resend_track(self):
        before = self.now_playing[1]
        time.sleep(5)
        if before == self.now_playing[1]:
            # if the track changed during the sleep, do not reassert it
            self.tm.send_music(self.now_playing[0], self.now_playing[1])

    def play_on_connected(self):
        time.sleep(5)
        self.play_music()

    def connect_player(self):
        if self.media_connected and self.media_player:
            obj = self.bus.get_object("org.bluez", self.media_player)
            media_interface = dbus.Interface(obj, "org.bluez.MediaPlayer1")
            self.pause_music = media_interface.get_dbus_method("Pause")
            self.play_music = media_interface.get_dbus_method("Play")
            self.play_pause_music = lambda: (self.play_music(), self.pause_music())
            self.next_music = media_interface.get_dbus_method("Next")
            self.prev_music = media_interface.get_dbus_method("Previous")
            self.player_executor.submit(self.play_on_connected)

    def on_audio_channel(self, channel):
        print("[player] selected audio channel {}".format(channel))
        if self.media_connected:
            if channel == 'bm':
                print("[player]: playing bt music")
                self.play_music()
            else:
                print("[player]: stopping bt music")
                self.pause_music()

    def on_button(self, key):
        print("[player] on_button "+key)
        if self.media_connected:
            if key == 'up':
                self.next_music()
            elif key == 'down':
                self.prev_music()
            elif key == 'mute':
                if not self.music_playing:
                    self.play_music()
                else:
                    self.pause_music()
            elif key == 'win':
                #play/pause
                self.play_pause_music()
                
        else:
            print("[player] media not connected, ignoring key {}".format(key))

    def fire_event(self, event, *args):
        if event not in self.listeners:
            return
        for listener in self.listeners[event]:
            listener(*args)

    def on_event(self, event, callback):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
        
    # Add Pairing Device
    def pair_new_device(self):
        # set device in pairing mode
        try:
            print("[player] Pairing new device...")
            adapter = self.bus.get_object("org.bluez", "/org/bluez/hci0")
            adapter_iface = dbus.Interface(adapter, "org.bluez.Adapter1")
            adapter_iface.StartDiscovery()
            print("[player] Pairing mode enabled.")
            
            # wait for a new device to pair with the system
            new_device = None
            while new_device is None:
                new_device = self.bus.get_object("org.bluez", "/org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX")
                time.sleep(1)
            print("[player] New device found.")
            
            # stop discovery
            adapter_iface.StopDiscovery()
            print("[player] Pairing mode disabled.")
            
            return True
        except dbus.DBusException as e:
            print(f"[error] Failed to pair new device: {e}")
            return
        
       # Remove Device
    def remove_device(self, mac_address):
        try:
            print(f"[player] Removing {mac_address} from paired devices...")
            adapter = self.bus.get_object("org.bluez", "/org/bluez/hci0")
            adapter_iface = dbus.Interface(adapter, "org.bluez.Adapter1")
            adapter_iface.RemoveDevice(f"/org/bluez/hci0/dev_{mac_address.replace(':', '_')}")
            print(f"[player] Device {mac_address} removed successfully.")
            return True
        except dbus.DBusException as e:
            print(f"[error] Failed to remove device {mac_address}: {e}")
            return False
