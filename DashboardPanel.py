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
        # If no message is provided, clear the instrument panel and close the menu
        if message is None:
            self.telemetry_manager.clear_dashboard()
            self.is_menu_open = False
        else:
            # Otherwise, send the message to the instrument panel and open the menu
            self.telemetry_manager.send_dashboard(message, show_arrows)
            self.is_menu_open = True
        # Trigger the 'menu_state_changed' event
        self.trigger_event('menu_state_changed', self.is_menu_open)

    def trigger_event(self, event, *args):
        # If the event has no listeners, return early
        if event not in self.event_listeners:
            return
        # Call each listener registered for the event
        for listener in self.event_listeners[event]:
            listener(*args)

    def register_event_listener(self, event, callback):
        # If the event has no listeners yet, initialize the listener list
        if event not in self.event_listeners:
            self.event_listeners[event] = []
        # Add the callback to the list of listeners for the event
        self.event_listeners[event].append(callback)

    def handle_phone_call(self, number):
        # If no number is provided, simulate hanging up the call
        if number is None:
            self.telemetry_manager.send_dashboard("  Hanging up!")
            time.sleep(1)
            self.telemetry_manager.clear_dashboard()
        else:
            # Otherwise, simulate answering the call
            self.telemetry_manager.send_dashboard("Hello? Hello!")
