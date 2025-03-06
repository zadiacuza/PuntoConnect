import can
import os
import time
import traceback
import subprocess

from MediaPlayer import MediaPlayer
from BodyControlModule import BodyControlModule
from HeartBeatLoop import HeartBeatLoop
from DashboardPanel import Dashboard
from MenuHandler import Menu
from PhoneHandler import PhoneHandler
from MessageHandler import MessageHandler


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
    
    body_control = BodyControlModule(bus)
    body_control.start()
    
    
    onehz_loop = HeartBeatLoop(bus)
    onehz_loop.start()

    textmessage = MessageHandler(bus)
    menu = Menu()
    player = MediaPlayer(textmessage)
    phone = PhoneHandler()
    btns = body_control.buttons
    dashpanel = Dashboard(textmessage)

    body_control.on_event('audio_channel', player.on_audio_channel)
    
    menu.on_event('item', dashpanel.on_menu)
    
    dashpanel.on_event('menu_opened', onehz_loop.on_menu_opened)
    dashpanel.on_event('menu_opened', btns.on_menu_opened)
    
    player.on_event('position', onehz_loop.on_bt_position)
    player.on_event('playing', onehz_loop.on_bt_playing)
    
    btns.on_event('menu', menu.on_button)
    btns.on_event('media', player.on_button)
    btns.on_event('phone', phone.on_button)
    
    phone.on_event('call', onehz_loop.on_phone)
    phone.on_event('call', btns.on_phone)
    phone.on_event('call', dashpanel.on_phone)

    print("Entering main loop")
    while True:
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("Shutting down...")
            body_control.shutdown()
            body_control.join()
            player.shutdown()
            bus.shutdown()
            exit(0)

except:
    ex = traceback.format_exc()
    # Debug.dump(ex)
