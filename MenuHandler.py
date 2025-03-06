import os
import time
import subprocess

class MenuOption:
    def __init__(self, label: str, action: callable, sub_options: list = None):
        self.label = label
        self.action = action
        self.sub_options = sub_options

    def select(self):
        self.action()

    def __getitem__(self, key):
        return self.sub_options[key]

    def __len__(self):
        return len(self.sub_options)

class Menu:
    current_options = []
    menu_structure = None

    def __init__(self):
        def close_menu():
            self.current_options = []
            self.update_display(None)

        def temporary_display(message, duration=2):
            self.update_display(message)
            time.sleep(duration)
            self.update_display(None)

        def confirm_shutdown():
            temporary_display("Are you sure?", 2)
            self.current_options.append(0)
            option = self.get_current_option()
            self.update_display(option.label, True)

        def shutdown_system():
            temporary_display("Shutting down...", 2)
            subprocess.run(['sudo', 'halt', 'now'])

        self.menu_structure = [
            MenuOption('Welcome', close_menu),
            MenuOption('Shutdown', confirm_shutdown, [
                MenuOption('Yes', shutdown_system),
                MenuOption('No', close_menu)
            ])
        ]

    def handle_button_press(self, key):
        print(f"[menu] key {key}")
        if key == 'menu':
            if len(self.current_options) == 0:
                self.current_options.append(0)
                option = self.get_current_option()
                self.update_display(option.label, True)
            else:
                option = self.get_current_option()
                option.select()
        elif key == 'up':
            if len(self.current_options) > 0:
                menu = self.get_current_menu()
                idx = self.current_options[-1]
                idx = (idx - 1) % len(menu)
                self.current_options[-1] = idx
                option = self.get_current_option()
                self.update_display(option.label, True)
        elif key == 'down':
            if len(self.current_options) > 0:
                menu = self.get_current_menu()
                idx = self.current_options[-1]
                idx = (idx + 1) % len(menu)
                self.current_options[-1] = idx
                option = self.get_current_option()
                self.update_display(option.label, True)
        elif key == 'mute':
            if len(self.current_options) > 0:
                self.current_options.pop()
                if len(self.current_options) > 0:
                    option = self.get_current_option()
                    self.update_display(option.label, True)
                else:
                    self.update_display(None)

    def get_current_option(self):
        option = self.menu_structure
        for idx in self.current_options:
            option = option[idx]
        return option

    def get_current_menu(self):
        menu = self.menu_structure
        for idx in self.current_options[:-1]:
            menu = menu[idx]
        return menu

    def update_display(self, message=None, show_arrows=False):
        print(f"[menu] {message}")
