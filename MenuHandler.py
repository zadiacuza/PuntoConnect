import os
import time
import subprocess

class MenuItem:
    def __init__(self, string: str, callback: callable, items: list = None):
        self.string = string
        self.callback = callback
        self.items = items

    def click(self):
        self.callback()

    def __getitem__(self, key):
        return self.items[key]

    def __len__(self):
        return len(self.items)

class Menu:
    active_items = []
    menu = None
    listeners = {}
    phone_calling = False

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

        def get_trusted_devices_callback():
            result = os.popen("bluetoothctl devices").read()
            devices = result.strip().split("\n")

            if not devices or devices == [""]:
                self.instpanel_display("No trusted devices")
                return
            
            trusted_devices = []
            for device in devices:
                parts = device.split(maxsplit=1)
                if len(parts) == 1:
                    trusted_devices.append(parts[1])
                else:
                    trusted_devices.append(parts[0])
            
            self.update_bluetooth_submenu(trusted_devices)

        def submenu_callback():
            self.active_items.append(0)
            item = self.get_active_item()
            self.instpanel_display(item.string, True)

        self.menu = [
            MenuItem('Hi Andy', dismiss_menu),
            MenuItem('Bluetooth', submenu_callback, [
                MenuItem('Devices', get_trusted_devices_callback),
            ]),
            MenuItem('Version', version_callback),
            MenuItem('Restart', restart_callback),
            MenuItem('Shutdown', shutdown_callback),
        ]

    def update_bluetooth_submenu(self, devices):
        bluetooth_menu = self.menu[1].items
        bluetooth_menu.clear()
        for device in devices:
            bluetooth_menu.append(MenuItem(device, lambda: self.instpanel_display(device, True), [
                MenuItem('Connect', lambda: self.connect_device(device)),
                MenuItem('Forget', lambda: self.forget_device(device))
            ]))
        bluetooth_menu.append(MenuItem('Back', lambda: self.active_items.pop()))

    def connect_device(self, device):
        self.instpanel_display(f"Connecting to {device}...")
        subprocess.run(["bluetoothctl", "connect", device])
        self.instpanel_display(f"Connected to {device}")

    def forget_device(self, device):
        self.instpanel_display(f"Forgetting {device}...")
        subprocess.run(["bluetoothctl", "remove", device])
        self.instpanel_display(f"Forgot {device}")

    def on_button(self, key):
        print("[menu] key {}".format(key))
        if key == 'menu':
            if len(self.active_items) == 0:
                self.active_items.append(0)
                item = self.get_active_item()
                self.instpanel_display(item.string, True)
                print("Menu open:\n{}".format(item.string))  # Added print statement

                

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
