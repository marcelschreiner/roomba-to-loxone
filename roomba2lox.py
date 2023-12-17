from time import sleep
import roombapy.const
from roombapy.roomba import Roomba
from roombapy.remote_client import RoombaRemoteClient
import socket
import json


# Insert the ip address and upd port of your Loxone Miniserver
LOXONE_IP = "192.168.1.23"
LOXONE_UDP_PORT = 1234


ROOMBA_STATES_ENUM = {
    "Charging": 0,
    "New Mission": 1,
    "Running": 2,
    "Recharging": 3,
    "Stuck": 4,
    "User Docking": 5,
    "Docking": 6,
    "Docking - End Mission": 7,
    "Cancelled": 8,
    "Stopped": 9,
    "Paused": 10,
    "End Mission": 11,
    "Emptying Bin": 12,
    "Base Unplugged": 13,
    "Unknown": 14,
}


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_key_by_value(my_dict, target_value, default_value):
    for key, value in my_dict.items():
        if value == target_value:
            return key
    return default_value


# Function to handle incoming UDP commands
def handle_udp_commands(cmd_raw, vacuum):
    cmd = cmd_raw.decode('utf-8')

    # Split command into command and value
    if cmd in ["start", "stop", "pause", "resume", "dock", "locate"]:
        if vacuum.current_state == "Stopped" and cmd == "start":
            vacuum.send_command("resume")
            sleep(0.1)
        elif vacuum.current_state == "Charging" and cmd == "resume":
            cmd = "start"
        vacuum.send_command(cmd)
    else:
        print("Invalid command received")


def send_state_to_loxone(message=None):
    try:
        message = json.dumps({"state_num": ROOMBA_STATES_ENUM[vacuum.current_state],
                              "state": vacuum.current_state,
                              "error_num": get_key_by_value(roombapy.const.ROOMBA_ERROR_MESSAGES, vacuum.error_message, 98),
                              "error": vacuum.error_message,
                              "battery": vacuum.master_state["state"]["reported"]["batPct"],
                              "bin_full": int(vacuum.master_state["state"]["reported"]["bin"]["full"]),
                              "rssi": vacuum.master_state["state"]["reported"]["signal"]["rssi"],
                              "snr": vacuum.master_state["state"]["reported"]["signal"]["snr"]})
        # print(message)

        # Send UDP packet to Loxone Miniserver
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(message, "utf-8"), (LOXONE_IP, LOXONE_UDP_PORT))
    except KeyError:
        pass


# Connect to Roomba vacuum
vacuum = Roomba(RoombaRemoteClient("10.1.7.41", "3193C20C20516840", ":1:1587554003:FjAKWUSsP90hfSZ9"))
vacuum.connect()
vacuum.register_on_message_callback(send_state_to_loxone)


# Create a UDP socket
my_ip_address = get_ip()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((my_ip_address, 8439))

try:
    print(f"Listening for commands on {my_ip_address}:8439")
    while True:
        data, address = s.recvfrom(4096)
        handle_udp_commands(data, vacuum)
except KeyboardInterrupt:
    vacuum.disconnect()
