import os
import os.path
import time
import subprocess
from trustedDevices import load_devices, create_devices_list
from BluetoothPlayer import BluetoothPlayer

class MenuItem:

    def __init__(self, string: str, callback: callable, items: list = None) -> object:
        self.string = string
        self.callback = callback
        self.items = items

    def click(self):
        self.callback()

    def __getitem__(self, key):
        return self.items[key]

    def __len__(self) -> int:
        return len(self.items)


class Menu:

    active_items = []
    menu = None
    listeners = {}
    phone_calling = False
    candumping = None
    bt_debug = False # Bluetooth debug mode
    devices = load_devices() # [{'name': "Andy's Galaxy S20 FE", 'mac_address': '98:B8:BC:36:80:EF'}, {'name': 'JBL Speaker', 'mac_address': 'AA:BB:CC:DD:EE:FF'}]
    player = BluetoothPlayer( tm=None)

    def __init__(self):
        if os.path.isfile('/otgstorage/readwrite'):
            fslabel = 'Make readonly'
            is_readwrite = True
        else:
            fslabel = 'Make readwrite'
            is_readwrite = False

        def dismiss_menu():
            self.active_items = []
            self.instpanel_display(None)

        def temp_show(message, sec=2):
            self.instpanel_display(message)
            time.sleep(sec)
            self.instpanel_display(None)

        def version_callback():
            result = subprocess.run(["dpkg-query", "--showformat='${Version}'", "--show", "infotainment"], stdout=subprocess.PIPE)
            infot_version = result.stdout.decode('UTF8').strip()

            result = subprocess.run(['uname', '-r'], stdout=subprocess.PIPE)
            kernel_version = result.stdout.decode('UTF8').strip()

            self.instpanel_display("{}/{}".format(infot_version, kernel_version))


        def restart_callback():
            temp_show("Restarting...", 2)
            subprocess.run(['sudo', 'systemctl', 'restart', 'infotainment'])

        def shutdown_callback():
            temp_show("Shutting down...", 2)
            subprocess.run(['sudo', 'halt', 'now'])

        def submenu_callback():
            self.active_items.append(0)
            item = self.get_active_item()
            self.instpanel_display(item.string, True)

        self.menu = [
            MenuItem('Hi Andy', dismiss_menu),
            MenuItem('Bluetooth', submenu_callback, [
                MenuItem('Devices', submenu_callback, [
                    # loop through devices json and create menu items
                    MenuItem(device['name'], submenu_callback, [
                        MenuItem('Connect', lambda: self.connect_device(device['mac_address'])),
                        MenuItem('Forget', lambda: self.forget_device(device['mac_address']))    
                    ]) for device in self.devices
                ]),
                MenuItem('add device', lambda: self.pair_device())            ]),
            MenuItem('Version', version_callback),
            MenuItem('Restart', restart_callback),
            MenuItem('Shutdown', shutdown_callback),
        ]


    def connect_device(self, mac_address):
        if self.bt_debug:
            print(f"Connecting to {mac_address}... (Debug Mode)")
            self.instpanel_display(f"Connecting..")
            time.sleep(2)
            print("Connected to device")
            self.instpanel_display(f"Connected")
            time.sleep(2)
            # dismiss menu
            self.active_items = []
            self.instpanel_display(None)
            
            return

        try:
            self.instpanel_display(f"Connecting to {mac_address}...")
            success = self.player.connect_device(mac_address)
            
            if success:
                print(f"Connected to {mac_address}")
                self.instpanel_display(f"Connected")
                time.sleep(2)
                print("dismiss menu")
                self.active_items = []
                self.instpanel_display(None)
            else:
                print(f"Connection failed for {mac_address}")
                self.instpanel_display(f"failed")
                time.sleep(2)
                self.active_items = []
                self.instpanel_display(None)

        except Exception as e:
            print(f"Error: {e}")
            self.instpanel_display(f"failed")
            time.sleep(2)
            self.active_items = []
            self.instpanel_display(None)


        except Exception as e:
            print(f"Error: {e}")
        print("Connected to device")
        self.instpanel_display(f"Connected")
        print("dismiss menu")
        self.active_items = []
        self.instpanel_display(None)

    def forget_device(self, device):
        self.instpanel_display(f"Removing {device}...")
        status = self.player.remove_device(device)
        
        if status:
            create_devices_list()
            self.devices = load_devices()
            self.instpanel_display(f"Device removed")
        else:
            self.instpanel_display(f"failed")
        time.sleep(2)
        print("dismiss menu")
        self.active_items = []
        self.instpanel_display(None)
        
    def pair_device(self):
        self.instpanel_display(f"Pairing device...")
        # discoverable on, pairable on, agent on
        status = self.player.pair_new_device()
        if status:
            print("Device paired")
            self.instpanel_display(f"Device paired")
        else:
            print("failed")
            self.instpanel_display(f"failed")
        time.sleep(2)
        print("dismiss menu")
        self.active_items = []
        self.instpanel_display(None)

    def on_button(self, key):
        print("[menu] key {}".format(key))
        if key == 'menu':
            if len(self.active_items) == 0:
                self.active_items.append(0)
                item = self.get_active_item()
                self.instpanel_display(item.string, True)

            else:
                item = self.get_active_item()
                item.click()

        elif key == 'up':
            if len(self.active_items) > 0:
                menu = self.get_active_menu()
                idx = self.active_items[-1]
                idx = (idx - 1) % len(menu)
                self.active_items[-1] = idx
                item = self.get_active_item()
                self.instpanel_display(item.string, True)

        elif key == 'down':
            if len(self.active_items) > 0:
                menu = self.get_active_menu()
                idx = self.active_items[-1]
                idx = (idx + 1) % len(menu)
                self.active_items[-1] = idx
                item = self.get_active_item()
                self.instpanel_display(item.string, True)

        elif key == 'mute':
            if len(self.active_items) > 0:
                self.active_items.pop()
                if len(self.active_items) > 0:
                    item = self.get_active_item()
                    self.instpanel_display(item.string, True)
                else:
                    self.instpanel_display(None)

    def get_active_item(self):
        item = self.menu
        for idx in self.active_items:
            item = item[idx]

        return item

    def get_active_menu(self):
        menu = self.menu
        for idx in self.active_items[0:-1]:
            menu = menu[idx]

        return menu

    def instpanel_display(self, message=None, show_arrows=False):
        print("[menu] {}".format(message))
        self.fire_event('item', message, show_arrows)

    def on_phone(self, number):
        if number is None:
            self.phone_calling = False
        else:
            self.phone_calling = True

    def fire_event(self, event, *args):
        if event not in self.listeners:
            return
        for listener in self.listeners[event]:
            listener(*args)

    def on_event(self, event, callback):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
