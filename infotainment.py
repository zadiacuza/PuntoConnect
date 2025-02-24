import can
import os
import time
import traceback
import subprocess


from BluetoothPlayer import BluetoothPlayer
from BodyComputerManager import BodyComputerManager
from CanOneHertzLoop import CanOneHertzLoop
from Debug import Debug
from InstrumentPanel import InstrumentPanel
from Menu import Menu
from PhoneManager import PhoneManager
from TextMessage import TextMessage
# from DoorStatus import DoorStatus


def is_can_interface_up(interface):
    result = subprocess.run(['ip', 'link', 'show', interface], capture_output=True, text=True)
    print(result.stdout)
    return 'UP' in result.stdout and 'state' in result.stdout

try:
    can_interface = 'vcan0' if os.uname()[4] == 'x86_64' else 'can0'
    
    if not is_can_interface_up(can_interface):
        print(f"CAN interface {can_interface} is not up. Please start it before running this script.")
        exit(1)
    
    bus = can.ThreadSafeBus(interface="socketcan", channel=can_interface, bitrate=50000)
    
    body_manager = BodyComputerManager(bus)
    body_manager.start()

    onehz_loop = CanOneHertzLoop(bus)
    onehz_loop.start()

    textmessage = TextMessage(bus)
    menu = Menu()
    player = BluetoothPlayer(textmessage)
    phone = PhoneManager()
    buttons = body_manager.buttons
    instpanel = InstrumentPanel(textmessage)
    # door_status = DoorStatus(textmessage)  # Create an instance of DoorStatus

    body_manager.on_event('audio_channel', player.on_audio_channel)

    menu.on_event('item', instpanel.on_menu)

    instpanel.on_event('menu_opened', onehz_loop.on_menu_opened)
    instpanel.on_event('menu_opened', buttons.on_menu_opened)

    player.on_event('position', onehz_loop.on_bt_position)
    player.on_event('playing', onehz_loop.on_bt_playing)

    buttons.on_event('menu',  menu.on_button)
    buttons.on_event('media', player.on_button)
    buttons.on_event('phone', phone.on_button)

    phone.on_event('call', onehz_loop.on_phone)
    phone.on_event('call', buttons.on_phone)
    phone.on_event('call', instpanel.on_phone)

    print("Entering main loop")
    while True:
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("Shutting down...")
            body_manager.shutdown()  # Stop the body manager thread
            body_manager.join()  # Wait for the body manager thread to finish
            print("Shutting down 2...")
            onehz_loop.shutdown()  # Stop the one-hertz loop
            onehz_loop.join()  # Wait for the loop to finish
            print("Shutting down 3...")
            player.shutdown()  # Shutdown the player
            bus.shutdown()  # Shutdown the CAN bus
            # os.system("sudo halt")  # Halt the system immediately after the loop ends
            exit(0)

except:
    ex = traceback.format_exc()
    Debug.dump(ex)
