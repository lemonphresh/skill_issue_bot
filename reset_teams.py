from bot import data, save_data

for team in data["teams"].values():
    team["points"] = 0
    team["unlocked_tiers"] = ["easy", "medium"]
    for board in team["boards"].values():
        for tile in board.values():
            tile["complete"] = False

save_data()
print("All teams have been reset.")