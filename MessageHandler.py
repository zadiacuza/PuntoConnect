import math
import time
import unidecode
from can import Message
from textwrap import wrap
from CANProtocol import *

class MessageHandler:
    END_OF_STRING = "000000"
    FIELD_SEPARATOR = "111111"
    CHAR_TO_BITSTRING = {
        "0": "000001", "1": "000010", "2": "000011", "3": "000100", "4": "000101",
        "5": "000110", "6": "000111", "7": "001000", "8": "001001", "9": "001010",
        ".": "001011", "A": "001100", "B": "001101", "C": "001110", "D": "001111",
        "E": "010000", "F": "010001", "G": "010010", "H": "010011", "I": "010100",
        "J": "010101", "K": "010110", "L": "010111", "M": "011000", "N": "011001",
        "O": "011010", "P": "011011", "Q": "011100", "R": "011101", "S": "011110",
        "T": "011111", "U": "100000", "V": "100001", "W": "100010", "X": "100011",
        "Y": "100100", "Z": "100101", "ñ": "100110", "ç": "100111", " ": "101000",
        "Ğ": "101001", "i": "101010", "j": "101011", "§": "101100", "À": "101101",
        "Ä": "101110", "ŭ": "101111", "Ü": "110000", "_": "110010", "?": "110101",
        "°": "110110", "!": "110111", "+": "111000", "-": "111001", ":": "111010",
        "/": "111011", "#": "111100", "*": "111101"
    }

    MENU_PREFIX_1 = "0001000000011010"
    MENU_PREFIX_2 = "0001000100011010"
    TEXT_PREFIX_1 = "0001000000010110"
    TEXT_PREFIX_2 = "0001000100010110"

    def __init__(self, bus):
        self.bus = bus
        self.BITSTRING_TO_CHAR = {v: k for k, v in self.CHAR_TO_BITSTRING.items()}

    def encode_dashboard_message(self, message, is_menu):
        bitstring = self.encode_string(message).ljust(96, '0')
        line1 = (self.MENU_PREFIX_1 if is_menu else self.TEXT_PREFIX_1) + bitstring[:48]
        line2 = (self.MENU_PREFIX_2 if is_menu else self.TEXT_PREFIX_2) + bitstring[48:]
        can_message1 = Message(arbitration_id=M162_MESSGS, data=self.bitstring_to_bytes(line1))
        can_message2 = Message(arbitration_id=M162_MESSGS, data=self.bitstring_to_bytes(line2))
        return can_message1, can_message2

    def encode_music_info(self, track, artist, folder=None):
        bitstring = self.encode_string(folder) if folder else self.END_OF_STRING
        bitstring += self.FIELD_SEPARATOR + self.encode_string(artist) + self.FIELD_SEPARATOR
        bitstring += self.encode_string(track, 18)
        messages = []
        num_messages = math.ceil(len(bitstring) / 48) - 1
        i = 0
        for chunk in wrap(bitstring, 48):
            chunk = chunk.ljust(48, '0')
            chunk = ba(hex='0x{}{}2A'.format(num_messages, i)).bin + chunk
            messages.append(Message(arbitration_id=M162_MESSGS, data=self.bitstring_to_bytes(chunk)))
            i += 1
        return messages

    def normalize_string(self, string, maxlen=14):
        string = string.rstrip().upper()
        if len(string) > maxlen:
            string = string[:maxlen]
        normalized = []
        for char in string:
            if char in self.CHAR_TO_BITSTRING:
                normalized.append(char)
            else:
                decoded = unidecode.unidecode(char)
                normalized.append(decoded if decoded in self.CHAR_TO_BITSTRING else ' ')
        return ''.join(normalized).replace('  ', ' ')

    def encode_string(self, string, maxlen=14):
        string = self.normalize_string(string, maxlen)
        return ''.join(self.CHAR_TO_BITSTRING[char] for char in string)

    def decode_messages(self, messages):
        bitstring = ""
        message_type = 'song' if messages[0][2] == '2' else 'dashboard'
        for message in messages:
            bitstring += ba(hex='0x' + message[4:]).bin
        return f"{message_type}: {self.decode_bitstring(bitstring)}"

    def decode_radio_message(self, message):
        bitstring = ba(hex='0x' + message).bin
        return self.decode_bitstring(bitstring)

    def decode_bitstring(self, bitstring):
        decoded = ""
        for bits in wrap(bitstring, 6):
            if len(bits) < 6:
                continue
            if bits == self.FIELD_SEPARATOR:
                decoded += "; "
            elif bits == self.END_OF_STRING:
                pass
            else:
                decoded += self.BITSTRING_TO_CHAR.get(bits, "?")
        return decoded

    def bitstring_to_bytes(self, s):
        return int(s, 2).to_bytes(len(s) // 8, byteorder='big')

    def display_on_dashboard(self, message, is_menu=False):
        print(f"Showing '{message}' on dashboard")
        messages = self.encode_dashboard_message(message, is_menu)
        self.bus.send(messages[0])
        time.sleep(0.01)
        self.bus.send(messages[1])

    def send_music_info(self, track, artist, folder=None):
        messages = self.encode_music_info(track, artist, folder)
        for message in messages:
            self.bus.send(message)
            time.sleep(0.01)

    def clear_dashboard(self):
        print("Clearing dashboard")
        self.bus.send(Message(arbitration_id=M162_MESSGS, data=bytearray(CLEAR_DASHPANEL_MESSG.bytes)))
