from FiatProtocol import MASK_DOOR_DRIVER, MASK_DOOR_PASSENGER

class DoorStatus:
    def __init__(self, tm):
        self.tm = tm  # Ensure tm is assigned to self.tm

    def check_door_status(self, payload):
        if payload & MASK_DOOR_DRIVER == MASK_DOOR_DRIVER:
            self.send_message("Goodday Andy")
        if payload & MASK_DOOR_PASSENGER == MASK_DOOR_PASSENGER:
            self.send_message("Hi Eleanor")

    def send_message(self, message):
        print(message)
        self.tm.send_instpanel(message)