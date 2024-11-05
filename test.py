import dolphin_memory_engine
import time

dolphin_memory_engine.hook()
roll = 20   

if int(roll) > 19:
    roll = 20
if int(roll) == 0:
    roll = 1
roll_hex = hex(int(roll))[2:]
while int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FD02, 1), byteorder='big') != 3:
    time.sleep(0.001)
while int.from_bytes(dolphin_memory_engine.read_bytes(0x801D40A2, 1), byteorder='big') != 0:
    time.sleep(0.001)
while int.from_bytes(dolphin_memory_engine.read_bytes(0x801D40A2, 1), byteorder='big') == 0:
    time.sleep(0.001)
Log_message('Triggering: Locked P4 Dice to ' + str(roll))
dolphin_memory_engine.write_bytes(0x801D40A2, int(roll_hex, 16).to_bytes(1, byteorder='big'))
