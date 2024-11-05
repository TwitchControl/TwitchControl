import dolphin_memory_engine
import random
import math
import time
import json5

def loadGame(event, log_message):
    with open('plugins/marioParty4/marioParty4.json5', 'r') as config_file:
            config = json5.load(config_file)

    reward_map = {reward["name"]: index for index, reward in enumerate(config["rewards"])}

    if event.reward.title == config["rewards"][reward_map["Add One Turn"]]["name"]:
        maxTurns = dolphin_memory_engine.read_bytes(0x8018FCFD, 1)
        maxTurnsPlusOne = int.from_bytes(maxTurns, byteorder='big') + 1
        if maxTurnsPlusOne > 50:
            maxTurnsPlusOne = 50
        dolphin_memory_engine.write_bytes(0x8018FCFD, maxTurnsPlusOne.to_bytes(1, byteorder='big'))
        log_message(f'Max Turns increased to: {maxTurnsPlusOne}')

    if event.reward.title == config["rewards"][reward_map["Wipe P1 Items"]]["name"]:
        dolphin_memory_engine.write_bytes(0x8018FC3D, (255).to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC3E, (255).to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC3F, (255).to_bytes(1, byteorder='big'))

    if event.reward.title == config["rewards"][reward_map["Wipe P2 Items"]]["name"]:
        dolphin_memory_engine.write_bytes(0x8018FC6D, (255).to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC6E, (255).to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC6F, (255).to_bytes(1, byteorder='big'))

    if event.reward.title == config["rewards"][reward_map["Wipe P3 Items"]]["name"]:
        dolphin_memory_engine.write_bytes(0x8018FC9D, (255).to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC9E, (255).to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC9F, (255).to_bytes(1, byteorder='big'))

    if event.reward.title == config["rewards"][reward_map["Wipe P4 Items"]]["name"]:
        dolphin_memory_engine.write_bytes(0x8018FCCD, (255).to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FCCE, (255).to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FCCF, (255).to_bytes(1, byteorder='big'))

    if event.reward.title == config["rewards"][reward_map["+20 Coins P1"]]["name"]:
        coinP1 = dolphin_memory_engine.read_bytes(0x8018FC54, 2)
        currentCoinsP1 = int.from_bytes(coinP1, byteorder='big')
        if currentCoinsP1 > 978:
            thirtyLostCoinsP1 = 999
        else:
            thirtyLostCoinsP1 = currentCoinsP1 + 20
        dolphin_memory_engine.write_bytes(0x8018FC54, thirtyLostCoinsP1.to_bytes(2, byteorder='big'))
        log_message(f'New Coins P1: {thirtyLostCoinsP1}')

    if event.reward.title == config["rewards"][reward_map["+20 Coins P2"]]["name"]:
        coinP2 = dolphin_memory_engine.read_bytes(0x8018FC84, 2)
        currentCoinsP2 = int.from_bytes(coinP2, byteorder='big')
        if currentCoinsP2 > 978:
            thirtyLostCoinsP2 = 999
        else:
            thirtyLostCoinsP2 = currentCoinsP2 + 20
        dolphin_memory_engine.write_bytes(0x8018FC84, thirtyLostCoinsP2.to_bytes(2, byteorder='big'))
        log_message(f'New Coins P2: {thirtyLostCoinsP2}')

    if event.reward.title == config["rewards"][reward_map["+20 Coins P3"]]["name"]:
        coinP3 = dolphin_memory_engine.read_bytes(0x8018FCB4, 2)
        currentCoinsP3 = int.from_bytes(coinP3, byteorder='big')
        if currentCoinsP3 > 978:
            thirtyLostCoinsP3 = 999
        else:
            thirtyLostCoinsP3 = currentCoinsP3 + 20
        dolphin_memory_engine.write_bytes(0x8018FCB4, thirtyLostCoinsP3.to_bytes(2, byteorder='big'))
        log_message(f'New Coins P3: {thirtyLostCoinsP3}')

    if event.reward.title == config["rewards"][reward_map["+20 Coins P4"]]["name"]:
        coinP4 = dolphin_memory_engine.read_bytes(0x8018FCE4, 2)
        currentCoinsP4 = int.from_bytes(coinP4, byteorder='big')
        if currentCoinsP4 > 978:
            thirtyLostCoinsP4 = 999
        else:
            thirtyLostCoinsP4 = currentCoinsP4 + 20
        dolphin_memory_engine.write_bytes(0x8018FCE4, thirtyLostCoinsP4.to_bytes(2, byteorder='big'))
        log_message(f'New Coins P4: {thirtyLostCoinsP4}')

    if event.reward.title == config["rewards"][reward_map["+1 Star P1"]]["name"]:
        coinP1 = dolphin_memory_engine.read_bytes(0x8018FC62, 2)
        thirtyLostCoinsP1 = int.from_bytes(coinP1, byteorder='big')
        if thirtyLostCoinsP1 > 998:
            thirtyLostCoinsP1 = 999
        else:
            thirtyLostCoinsP1 = thirtyLostCoinsP1 + 1
        dolphin_memory_engine.write_bytes(0x8018FC62, thirtyLostCoinsP1.to_bytes(2, byteorder='big'))
        log_message(f'New Stars P1: {thirtyLostCoinsP1}')

    if event.reward.title == config["rewards"][reward_map["+1 Star P2"]]["name"]:
        coinP2 = dolphin_memory_engine.read_bytes(0x8018FC92, 2)
        thirtyLostCoinsP2 = int.from_bytes(coinP2, byteorder='big')
        if thirtyLostCoinsP2 > 998:
            thirtyLostCoinsP2 = 999
        else:
            thirtyLostCoinsP2 = thirtyLostCoinsP2 + 1
        dolphin_memory_engine.write_bytes(0x8018FC92, thirtyLostCoinsP2.to_bytes(2, byteorder='big'))
        log_message(f'New Stars P2: {thirtyLostCoinsP2}')

    if event.reward.title == config["rewards"][reward_map["+1 Star P3"]]["name"]:
        coinP3 = dolphin_memory_engine.read_bytes(0x8018FCC2, 2)
        thirtyLostCoinsP3 = int.from_bytes(coinP3, byteorder='big')
        if thirtyLostCoinsP3 > 998:
            thirtyLostCoinsP3 = 999
        else:
            thirtyLostCoinsP3 = thirtyLostCoinsP3 + 1
        dolphin_memory_engine.write_bytes(0x8018FCC2, thirtyLostCoinsP3.to_bytes(2, byteorder='big'))
        log_message(f'New Stars P3: {thirtyLostCoinsP3}')

    if event.reward.title == config["rewards"][reward_map["+1 Star P4"]]["name"]:
        coinP4 = dolphin_memory_engine.read_bytes(0x8018FCF2, 2)
        thirtyLostCoinsP4 = int.from_bytes(coinP4, byteorder='big')
        if thirtyLostCoinsP4 > 998:
            thirtyLostCoinsP4 = 999
        else:
            thirtyLostCoinsP4 = thirtyLostCoinsP4 + 1
        dolphin_memory_engine.write_bytes(0x8018FCF2, thirtyLostCoinsP4.to_bytes(2, byteorder='big'))
        log_message(f'New Stars P4: {thirtyLostCoinsP4}')

    if event.reward.title == config["rewards"][reward_map["Coin Revolution"]]["name"]:
        coinP1 = dolphin_memory_engine.read_bytes(0x8018FC54, 2)
        coinP2 = dolphin_memory_engine.read_bytes(0x8018FC84, 2)
        coinP3 = dolphin_memory_engine.read_bytes(0x8018FCB4, 2)
        coinP4 = dolphin_memory_engine.read_bytes(0x8018FCE4, 2)
        totalCoins = (int.from_bytes(coinP1, byteorder='big') +
                      int.from_bytes(coinP2, byteorder='big') + 
                      int.from_bytes(coinP3, byteorder='big') + 
                      int.from_bytes(coinP4, byteorder='big'))
        revParsed = math.floor(totalCoins / 4)
        dolphin_memory_engine.write_bytes(0x8018FC54, revParsed.to_bytes(2, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC84, revParsed.to_bytes(2, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FCB4, revParsed.to_bytes(2, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FCE4, revParsed.to_bytes(2, byteorder='big'))
        log_message(f'New Coins after Revolution: {revParsed}')

    if event.reward.title == config["rewards"][reward_map["Star Revolution"]]["name"]:
        coinP1 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC62, 2), byteorder='big')
        coinP2 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC92, 2), byteorder='big')
        coinP3 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FCC2, 2), byteorder='big')
        coinP4 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FCF2, 2), byteorder='big')
        totalCoins = coinP1 + coinP2 + coinP3 + coinP4
        baseAmount = totalCoins // 4
        excessCoins = totalCoins % 4
        dolphin_memory_engine.write_bytes(0x8018FC62, baseAmount.to_bytes(2, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC92, baseAmount.to_bytes(2, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FCC2, baseAmount.to_bytes(2, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FCF2, baseAmount.to_bytes(2, byteorder='big'))
        if excessCoins > 0:
            players = ['P1', 'P2', 'P3', 'P4']
            chosen_players = random.sample(players, excessCoins)
            for player in chosen_players:
                if player == 'P1':
                    dolphin_memory_engine.write_bytes(0x8018FC62, (baseAmount + 1).to_bytes(2, byteorder='big'))
                elif player == 'P2':
                    dolphin_memory_engine.write_bytes(0x8018FC92, (baseAmount + 1).to_bytes(2, byteorder='big'))
                elif player == 'P3':
                    dolphin_memory_engine.write_bytes(0x8018FCC2, (baseAmount + 1).to_bytes(2, byteorder='big'))
                elif player == 'P4':
                    dolphin_memory_engine.write_bytes(0x8018FCF2, (baseAmount + 1).to_bytes(2, byteorder='big'))
            log_message(f'Excess coins distributed to: {", ".join(chosen_players)}')
        else:
            log_message("No excess coins to distribute.")

    if event.reward.title == config["rewards"][reward_map["Give P1 1 Item"]]["name"]:
        item1 = dolphin_memory_engine.read_bytes(0x8018FC3F, 1)
        item2 = dolphin_memory_engine.read_bytes(0x8018FC3F, 1)
        item3 = dolphin_memory_engine.read_bytes(0x8018FC3F, 1)
        if config["rewards"][reward_map["Give P1 1 Item"]]["dxItems"] == "True":
            hex_values = [
                "00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
                "0A", "0B", "0C", "0E", "0F", "10", "11", "12", "13", "14",
                "15", "16", "17", "18", "19", "1A", "1B", "1C", "1D", "1E",
                "1F", "20", "21", "22", "23"
            ]
        else:
            hex_values = [
                "00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
                "0A", "0B", "0C"
            ]
        random_hex = random.choice(hex_values)
        if int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC3D, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FC3D, int(random_hex, 16).to_bytes(1, byteorder='big'))
        elif int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC3E, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FC3E, int(random_hex, 16).to_bytes(1, byteorder='big'))
        elif int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC3F, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FC3F, int(random_hex, 16).to_bytes(1, byteorder='big'))

    if event.reward.title == config["rewards"][reward_map["Give P2 1 Item"]]["name"]:
        item1 = dolphin_memory_engine.read_bytes(0x8018FC6F, 1)
        item2 = dolphin_memory_engine.read_bytes(0x8018FC6F, 1)
        item3 = dolphin_memory_engine.read_bytes(0x8018FC6F, 1)
        if config["rewards"][reward_map["Give P2 1 Item"]]["dxItems"] == "True":
            hex_values = [
                "00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
                "0A", "0B", "0C", "0E", "0F", "10", "11", "12", "13", "14",
                "15", "16", "17", "18", "19", "1A", "1B", "1C", "1D", "1E",
                "1F", "20", "21", "22", "23"
            ]
        else:
            hex_values = [
                "00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
                "0A", "0B", "0C"
            ]
        random_hex = random.choice(hex_values)
        if int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC6D, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FC6D, int(random_hex, 16).to_bytes(1, byteorder='big'))
        elif int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC6E, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FC6E, int(random_hex, 16).to_bytes(1, byteorder='big'))
        elif int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC6F, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FC6F, int(random_hex, 16).to_bytes(1, byteorder='big'))

    if event.reward.title == config["rewards"][reward_map["Give P3 1 Item"]]["name"]:
        item1 = dolphin_memory_engine.read_bytes(0x8018FC9F, 1)
        item2 = dolphin_memory_engine.read_bytes(0x8018FC9F, 1)
        item3 = dolphin_memory_engine.read_bytes(0x8018FC9F, 1)
        if config["rewards"][reward_map["Give P3 1 Item"]]["dxItems"] == "True":
            hex_values = [
                "00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
                "0A", "0B", "0C", "0E", "0F", "10", "11", "12", "13", "14",
                "15", "16", "17", "18", "19", "1A", "1B", "1C", "1D", "1E",
                "1F", "20", "21", "22", "23"
            ]
        else:
            hex_values = [
                "00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
                "0A", "0B", "0C"
            ]
        random_hex = random.choice(hex_values)
        if int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC9D, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FC9D, int(random_hex, 16).to_bytes(1, byteorder='big'))
        elif int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC9E, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FC9E, int(random_hex, 16).to_bytes(1, byteorder='big'))
        elif int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC9F, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FC9F, int(random_hex, 16).to_bytes(1, byteorder='big'))

    if event.reward.title == config["rewards"][reward_map["Give P4 1 Item"]]["name"]:
        item1 = dolphin_memory_engine.read_bytes(0x8018FCCF, 1)
        item2 = dolphin_memory_engine.read_bytes(0x8018FCCF, 1)
        item3 = dolphin_memory_engine.read_bytes(0x8018FCCF, 1)
        if config["rewards"][reward_map["Give P4 1 Item"]]["dxItems"] == "True":
            hex_values = [
                "00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
                "0A", "0B", "0C", "0E", "0F", "10", "11", "12", "13", "14",
                "15", "16", "17", "18", "19", "1A", "1B", "1C", "1D", "1E",
                "1F", "20", "21", "22", "23"
            ]
        else:
            hex_values = [
                "00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
                "0A", "0B", "0C"
            ]
        random_hex = random.choice(hex_values)
        if int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FCCD, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FCCD, int(random_hex, 16).to_bytes(1, byteorder='big'))
        elif int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FCCE, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FCCE, int(random_hex, 16).to_bytes(1, byteorder='big'))
        elif int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FCCF, 1), byteorder='big') == 255:
            dolphin_memory_engine.write_bytes(0x8018FCCF, int(random_hex, 16).to_bytes(1, byteorder='big'))

    if event.reward.title == config["rewards"][reward_map["-20 Coins P1"]]["name"]:
        coinP1 = dolphin_memory_engine.read_bytes(0x8018FC54, 2)
        currentCoinsP1 = int.from_bytes(coinP1, byteorder='big')
        if currentCoinsP1 < 20:
            thirtyLostCoinsP1 = 0
        else:
            thirtyLostCoinsP1 = currentCoinsP1 - 20
        dolphin_memory_engine.write_bytes(0x8018FC54, thirtyLostCoinsP1.to_bytes(2, byteorder='big'))
        log_message(f'New Coins P1: {thirtyLostCoinsP1}')

    if event.reward.title == config["rewards"][reward_map["-20 Coins P2"]]["name"]:
        coinP2 = dolphin_memory_engine.read_bytes(0x8018FC84, 2)
        currentCoinsP2 = int.from_bytes(coinP2, byteorder='big')
        if currentCoinsP2 < 20:
            thirtyLostCoinsP3 = 0
        else:
            thirtyLostCoinsP2 = currentCoinsP2 - 20
        dolphin_memory_engine.write_bytes(0x8018FC84, thirtyLostCoinsP2.to_bytes(2, byteorder='big'))
        log_message(f'New Coins P2: {thirtyLostCoinsP2}')

    if event.reward.title == config["rewards"][reward_map["-20 Coins P3"]]["name"]:
        coinP3 = dolphin_memory_engine.read_bytes(0x8018FCB4, 2)
        currentCoinsP3 = int.from_bytes(coinP3, byteorder='big')
        if currentCoinsP3 < 20:
            thirtyLostCoinsP3 = 0
        else:
            thirtyLostCoinsP3 = currentCoinsP3 - 20
        dolphin_memory_engine.write_bytes(0x8018FCB4, thirtyLostCoinsP3.to_bytes(2, byteorder='big'))
        log_message(f'New Coins P3: {thirtyLostCoinsP3}')

    if event.reward.title == config["rewards"][reward_map["-20 Coins P4"]]["name"]:
        coinP4 = dolphin_memory_engine.read_bytes(0x8018FCE4, 2)
        currentCoinsP4 = int.from_bytes(coinP4, byteorder='big')
        if currentCoinsP4 < 20:
            thirtyLostCoinsP4 = 0
        else:
            thirtyLostCoinsP4 = currentCoinsP4 - 20
        dolphin_memory_engine.write_bytes(0x8018FCE4, thirtyLostCoinsP4.to_bytes(2, byteorder='big'))
        log_message(f'New Coins P4: {thirtyLostCoinsP4}')

    if event.reward.title == config["rewards"][reward_map["-1 Star P1"]]["name"]:
        coinP1 = dolphin_memory_engine.read_bytes(0x8018FC62, 2)
        thirtyLostCoinsP1 = int.from_bytes(coinP1, byteorder='big')
        if thirtyLostCoinsP1 < 1:
            thirtyLostCoinsP1 = 0
        else:
            thirtyLostCoinsP1 = thirtyLostCoinsP1 - 1
        dolphin_memory_engine.write_bytes(0x8018FC62, thirtyLostCoinsP1.to_bytes(2, byteorder='big'))
        log_message(f'New Stars P1: {thirtyLostCoinsP1}')

    if event.reward.title == config["rewards"][reward_map["-1 Star P2"]]["name"]:
        coinP2 = dolphin_memory_engine.read_bytes(0x8018FC92, 2)
        thirtyLostCoinsP2 = int.from_bytes(coinP2, byteorder='big')
        if thirtyLostCoinsP2 < 1:
            thirtyLostCoinsP2 = 0
        else:
            thirtyLostCoinsP2 = thirtyLostCoinsP2 - 1
        dolphin_memory_engine.write_bytes(0x8018FC92, thirtyLostCoinsP2.to_bytes(2, byteorder='big'))
        log_message(f'New Stars P2: {thirtyLostCoinsP2}')

    if event.reward.title == config["rewards"][reward_map["-1 Star P3"]]["name"]:
        coinP3 = dolphin_memory_engine.read_bytes(0x8018FCC2, 2)
        thirtyLostCoinsP3 = int.from_bytes(coinP3, byteorder='big')
        if thirtyLostCoinsP3 < 1:
            thirtyLostCoinsP3 = 0
        else:
            thirtyLostCoinsP3 = thirtyLostCoinsP3 - 1
        dolphin_memory_engine.write_bytes(0x8018FCC2, thirtyLostCoinsP3.to_bytes(2, byteorder='big'))
        log_message(f'New Stars P3: {thirtyLostCoinsP3}')

    if event.reward.title == config["rewards"][reward_map["-1 Star P4"]]["name"]:
        coinP4 = dolphin_memory_engine.read_bytes(0x8018FCF2, 2)
        thirtyLostCoinsP4 = int.from_bytes(coinP4, byteorder='big')
        if thirtyLostCoinsP4 < 1:
            thirtyLostCoinsP4 = 0
        else:
            thirtyLostCoinsP4 = thirtyLostCoinsP4 - 1
        dolphin_memory_engine.write_bytes(0x8018FCF2, thirtyLostCoinsP4.to_bytes(2, byteorder='big'))
        log_message(f'New Stars P4: {thirtyLostCoinsP4}')

    if event.reward.title == config["rewards"][reward_map["Redistribute ALL Items"]]["name"]:
        p1Item1 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC3D, 1), byteorder='big')
        p1Item2 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC3E, 1), byteorder='big')
        p1Item3 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC3F, 1), byteorder='big')
        p2Item1 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC6D, 1), byteorder='big')
        p2Item2 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC6E, 1), byteorder='big')
        p2Item3 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC6F, 1), byteorder='big')
        p3Item1 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC9D, 1), byteorder='big')
        p3Item2 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC9E, 1), byteorder='big')
        p3Item3 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FC9F, 1), byteorder='big')
        p4Item1 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FCCD, 1), byteorder='big')
        p4Item2 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FCCE, 1), byteorder='big')
        p4Item3 = int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FCCF, 1), byteorder='big')
        hex_values = [
            p1Item1, p1Item2, p1Item3,
            p2Item1, p2Item2, p2Item3,
            p3Item1, p3Item2, p3Item3,
            p4Item1, p4Item2, p4Item3
        ]
        random_selections = random.sample(hex_values, 12)
        hex_values_p1 = [
            random_selections[0], random_selections[1], random_selections[2]
        ]
        hex_values_p2 = [
            random_selections[3], random_selections[4], random_selections[5]
        ]
        hex_values_p3 = [
            random_selections[6], random_selections[7], random_selections[8]
        ]
        hex_values_p4 = [
            random_selections[9], random_selections[10], random_selections[11]
        ]
        hex_values_p1.sort()
        hex_values_p2.sort()
        hex_values_p3.sort()
        hex_values_p4.sort()
        dolphin_memory_engine.write_bytes(0x8018FC3D, hex_values_p1[0].to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC3E, hex_values_p1[1].to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC3F, hex_values_p1[2].to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC6D, hex_values_p2[0].to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC6E, hex_values_p2[1].to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC6F, hex_values_p2[2].to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC9D, hex_values_p3[0].to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC9E, hex_values_p3[1].to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FC9F, hex_values_p3[2].to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FCCD, hex_values_p4[0].to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FCCE, hex_values_p4[1].to_bytes(1, byteorder='big'))
        dolphin_memory_engine.write_bytes(0x8018FCCF, hex_values_p4[2].to_bytes(1, byteorder='big'))
        log_message('Item Revolution Complete')

    if event.reward.title == config["rewards"][reward_map["Lock P1 Dice"]]["name"]:
        roll = event.input
        if int(roll) > 19:
            roll = 20
        if int(roll) == 0:
            roll = 1
        roll_hex = hex(int(roll))[2:]
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FD02, 1), byteorder='big') != 0:
            time.sleep(0.05)
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x801D40A2, 1), byteorder='big') != 0:
            time.sleep(0.05)
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x801D40A2, 1), byteorder='big') == 0:
            time.sleep(0.05)
        Log_message('Triggering: Locked P4 Dice to ' + str(roll))
        dolphin_memory_engine.write_bytes(0x801D40A2, int(roll_hex, 16).to_bytes(1, byteorder='big'))



    if event.reward.title == config["rewards"][reward_map["Lock P2 Dice"]]["name"]:
        roll = event.input
        if int(roll) > 19:
            roll = 20
        if int(roll) == 0:
            roll = 1
        roll_hex = hex(int(roll))[2:]
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FD02, 1), byteorder='big') != 1:
            time.sleep(0.05)
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x801D40A2, 1), byteorder='big') != 0:
            time.sleep(0.05)
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x801D40A2, 1), byteorder='big') == 0:
            time.sleep(0.05)
        Log_message('Triggering: Locked P2 Dice to ' + str(roll))
        dolphin_memory_engine.write_bytes(0x801D40A2, int(roll_hex, 16).to_bytes(1, byteorder='big'))



    if event.reward.title == config["rewards"][reward_map["Lock P3 Dice"]]["name"]:
        roll = event.input
        if int(roll) > 19:
            roll = 20
        if int(roll) == 0:
            roll = 1
        roll_hex = hex(int(roll))[2:]
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FD02, 1), byteorder='big') != 2:
            time.sleep(0.05)
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x801D40A2, 1), byteorder='big') != 0:
            time.sleep(0.05)
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x801D40A2, 1), byteorder='big') == 0:
            time.sleep(0.05)
        Log_message('Triggering: Locked P3 Dice to ' + str(roll))
        dolphin_memory_engine.write_bytes(0x801D40A2, int(roll_hex, 16).to_bytes(1, byteorder='big'))



    if event.reward.title == config["rewards"][reward_map["Lock P4 Dice"]]["name"]:
        roll = event.input
        if int(roll) > 19:
            roll = 20
        if int(roll) == 0:
            roll = 1
        roll_hex = hex(int(roll))[2:]
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x8018FD02, 1), byteorder='big') != 3:
            time.sleep(0.05)
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x801D40A2, 1), byteorder='big') != 0:
            time.sleep(0.05)
        while int.from_bytes(dolphin_memory_engine.read_bytes(0x801D40A2, 1), byteorder='big') == 0:
            time.sleep(0.05)
        Log_message('Triggering: Locked P4 Dice to ' + str(roll))
        dolphin_memory_engine.write_bytes(0x801D40A2, int(roll_hex, 16).to_bytes(1, byteorder='big'))
