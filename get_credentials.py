# 1. Before running this script ensure that no other Roomba controller (App on smartphone, Home Assistant, ...) is running!
# 2. Then enter pairing mode on Roomba by pressing home button and locate button for a few seconds.
# 3. Run this script

from roombapy.discovery import RoombaDiscovery
from roombapy.getpassword import RoombaPassword

# Enter the IP of your Roomba vacuum
IP_OF_ROOMBA_VACUUM = "192.168.0.123"

discovery = RoombaDiscovery()
for vacuum in discovery.get_all():
    if vacuum.ip == IP_OF_ROOMBA_VACUUM:
        password = RoombaPassword(IP_OF_ROOMBA_VACUUM)
        print(f"Credentials for {vacuum.robot_name}:")
        print(f"  IP:       {vacuum.ip}")
        print(f"  Password: {password.get_password()}")
        print(f"  Blid:     {vacuum.blid}")
