import dolphin_memory_engine
import random
import math
import time
from functions import read_bytes, write_bytes, update_value

def loadGame(config, event, log_message):
    reward_title = event.reward.title

    def distribute_excess_coins(base_address, total_coins, num_players=4):
        base_amount = total_coins // num_players
        excess_coins = total_coins % num_players
        addresses = [base_address + i * 0x30 for i in range(num_players)]
        for address in addresses:
            write_bytes(address, base_amount, 2)
        if excess_coins > 0:
            chosen_players = random.sample(range(num_players), excess_coins)
            for player in chosen_players:
                write_bytes(addresses[player], base_amount + 1, 2)
            log_message(f'Excess coins distributed to players: {chosen_players}')
        else:
            log_message("No excess coins to distribute.")

    if reward_title == "Add One Turn":
        max_turns = read_bytes(0x8018FCFD)
        max_turns_plus_one = min(max_turns + 1, 50)
        write_bytes(0x8018FCFD, max_turns_plus_one)
        log_message(f'Max Turns increased to: {max_turns_plus_one}')

    elif reward_title in ["Wipe P1 Items", "Wipe P2 Items", "Wipe P3 Items", "Wipe P4 Items"]:
        player_index = ["Wipe P1 Items", "Wipe P2 Items", "Wipe P3 Items", "Wipe P4 Items"].index(reward_title)
        base_address = 0x8018FC3D + player_index * 0x30
        for offset in range(3):
            write_bytes(base_address + offset, 255)

    elif reward_title in ["+20 Coins P1", "+20 Coins P2", "+20 Coins P3", "+20 Coins P4"]:
        player_index = ["+20 Coins P1", "+20 Coins P2", "+20 Coins P3", "+20 Coins P4"].index(reward_title)
        address = 0x8018FC54 + player_index * 0x30
        new_coins = update_value(address, 20, 0, 999)
        log_message(f'New Coins P{player_index + 1}: {new_coins}')

    elif reward_title in ["+1 Star P1", "+1 Star P2", "+1 Star P3", "+1 Star P4"]:
        player_index = ["+1 Star P1", "+1 Star P2", "+1 Star P3", "+1 Star P4"].index(reward_title)
        address = 0x8018FC62 + player_index * 0x30
        new_stars = update_value(address, 20, 0, 999)
        log_message(f'New Stars P{player_index + 1}: {new_stars}')

    elif reward_title == "Coin Revolution":
        total_coins = sum(read_bytes(0x8018FC54 + i * 0x30, 2) for i in range(4))
        distribute_excess_coins(0x8018FC54, total_coins)

    elif reward_title == "Star Revolution":
        total_stars = sum(read_bytes(0x8018FC62 + i * 0x30, 2) for i in range(4))
        distribute_excess_coins(0x8018FC62, total_stars)

    elif reward_title in ["Give P1 1 Item", "Give P2 1 Item", "Give P3 1 Item", "Give P4 1 Item"]:
        player_index = ["Give P1 1 Item", "Give P2 1 Item", "Give P3 1 Item", "Give P4 1 Item"].index(reward_title)
        base_address = 0x8018FC3D + player_index * 0x30
        dx_items = config["rewards"][15]["dxItems"] == "True"
        hex_values = [f"{i:02X}" for i in range(0x24 if dx_items else 0x0D)]
        random_hex = random.choice(hex_values)
        for offset in range(3):
            if read_bytes(base_address + offset) == 255:
                write_bytes(base_address + offset, int(random_hex, 16))
                break

    elif reward_title in ["-20 Coins P1", "-20 Coins P2", "-20 Coins P3", "-20 Coins P4"]:
        player_index = ["-20 Coins P1", "-20 Coins P2", "-20 Coins P3", "-20 Coins P4"].index(reward_title)
        address = 0x8018FC54 + player_index * 0x30
        new_coins = update_value(address, -20, 0, 999)
        log_message(f'New Coins P{player_index + 1}: {new_coins}')

    elif reward_title in ["-1 Star P1", "-1 Star P2", "-1 Star P3", "-1 Star P4"]:
        player_index = ["-1 Star P1", "-1 Star P2", "-1 Star P3", "-1 Star P4"].index(reward_title)
        address = 0x8018FC62 + player_index * 0x30
        new_stars = update_value(address, -1, 0, 999)
        log_message(f'New Stars P{player_index + 1}: {new_stars}')

    elif reward_title == "Redistribute ALL Items":
        items = [read_bytes(0x8018FC3D + i * 0x30 + j) for i in range(4) for j in range(3)]
        random.shuffle(items)
        for i in range(4):
            sorted_items = sorted(items[i * 3:(i + 1) * 3])
            for j, item in enumerate(sorted_items):
                write_bytes(0x8018FC3D + i * 0x30 + j, item)
        log_message('Item Revolution Complete')

    elif reward_title in ["Lock P1 Dice", "Lock P2 Dice", "Lock P3 Dice", "Lock P4 Dice"]:
        player_index = ["Lock P1 Dice", "Lock P2 Dice", "Lock P3 Dice", "Lock P4 Dice"].index(reward_title)
        roll = max(1, min(event.input, 20))
        roll_hex = int(roll)
        while read_bytes(0x8018FD02) != player_index:
            time.sleep(0.2)
        while read_bytes(0x801D40A2) == 0:
            write_bytes(0x80086970, 26)
            write_bytes(0x80086971, 0)
            write_bytes(0x80086972, 0)
            write_bytes(0x80086973, roll_hex)
            time.sleep(0.2)
            log_message(f'Triggering: Locked P{player_index + 1} Dice to {roll}')