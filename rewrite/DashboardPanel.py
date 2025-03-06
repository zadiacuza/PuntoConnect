import time

class Dashboard:
    # Dictionary to store event listeners
    event_listeners = {}
    # Variable to hold the telemetry manager instance
    telemetry_manager = None
    # Flag to indicate if the menu is open
    is_menu_open = False

    def __init__(self, telemetry_manager):
        # Initialize the telemetry manager
        self.telemetry_manager = telemetry_manager

    def handle_menu(self, message, show_arrows):
        if message is None:
            self._close_menu()
        else:
            self._open_menu(message, show_arrows)
        self.trigger_event('menu_state_changed', self.is_menu_open)

    def _close_menu(self):
        self.telemetry_manager.clear_dashboard()
        self.is_menu_open = False

    def _open_menu(self, message, show_arrows):
        self.telemetry_manager.send_dashboard(message, show_arrows)
        self.is_menu_open = True

    def trigger_event(self, event, *args):
        if event not in self.event_listeners:
            return
        for listener in self.event_listeners[event]:
            listener(*args)

    def register_event_listener(self, event, callback):
        if event not in self.event_listeners:
            self.event_listeners[event] = []
        self.event_listeners[event].append(callback)

    def handle_phone_call(self, number):
        if number is None:
            self._hang_up_call()
        else:
            self._answer_call()

    def _hang_up_call(self):
        self.telemetry_manager.send_dashboard("  Hanging up!")
        time.sleep(1)
        self.telemetry_manager.clear_dashboard()

    def _answer_call(self):
        self.telemetry_manager.send_dashboard("Hello? Hello!")
