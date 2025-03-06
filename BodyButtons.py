import time
# import subprocess

class BodyButtons:
    # Dictionary to store event listeners
    listeners = {}
    # Dictionary to manage debouncing of button presses
    debouncers = {}

    phone_calling = False
    menu_opened = False

    def handle_debounce(self, button):
        """
        Handle button press with debounce logic.
        
        Parameters:
        button (str): The button that was pressed.
        """
        # Check if the button was pressed recently to debounce
        if button in self.debouncers:
            if time.time() - self.debouncers[button] < 0.3:
                return

        # Update the last press time for the button
        self.debouncers[button] = time.time()
        # Fire a generic button event
        self.trigger_event('button', button)

        # Handle specific button actions
        if button == 'menu':
            if self.phone_calling:
                print("[buttons] phone")
                self.trigger_event('phone', button)
            else:
                print("[buttons] menu")
                self.trigger_event('menu', button)

        if button in ['up', 'down', 'mute']:
            if self.menu_opened:
                print("[buttons] menu")
                self.trigger_event('menu', button)
            else:
                print("[buttons] media")
                self.trigger_event('media', button)
                
                # Windows button → Trigger Assistant
        if button == 'win':
            print("[buttons] triggering assistant")
            self.trigger_event('assistant')
            # self.trigger_google_assistant()

    # def trigger_google_assistant(self):
    #     """
    #     Trigger Google Assistant on the phone over Bluetooth.
    #     """
    #     try:
    #         subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_ASSIST'])
    #         print("[assistant] Google Assistant triggered over Bluetooth")
    #     except Exception as e:
    #         print(f"[assistant] Failed to trigger Google Assistant: {e}")

    def update_phone_status(self, number):
        """
        Update the phone calling status.
        
        Parameters:
        number (str or None): The phone number if a call is active, None if no call.
        """
        self.phone_calling = number is not None

    def update_menu_status(self, is_open):
        """
        Update the menu opened status.
        
        Parameters:
        is_open (bool): True if the menu is opened, False otherwise.
        """
        self.menu_opened = is_open

    def trigger_event(self, event, *args):
        """
        Fire an event to all registered listeners.
        
        Parameters:
        event (str): The name of the event to fire.
        *args: Additional arguments to pass to the event listeners.
        """
        if event not in self.listeners:
            return
        for listener in self.listeners[event]:
            listener(*args)

    def register_event_listener(self, event, callback):
        """
        Register an event listener.
        
        Parameters:
        event (str): The name of the event to listen for.
        callback (callable): The function to call when the event is fired.
        """
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)


