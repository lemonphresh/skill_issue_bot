import json
import os
from discord.ext import commands
import config 
import asyncio

DATA_FILE = "skill_issue_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"teams": {}, "tier_thresholds": {"easy": 0, "medium": 0, "hard": 20, "elite": 40, "master": 65, "gm": 100}, "tile_points": {"easy": 1, "medium": 2, "hard": 3, "elite": 4, "master": 5, "gm": 6}}

def save_data():
    backup_file = f"backup_{DATA_FILE}"
    with open(backup_file, "w") as f:
        json.dump(data, f, indent=2)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def visualize_board(board):
    size = int(len(board) ** 0.5)
    msg = ""
    for row in range(size):
        row_letter = chr(ord('A') + row)
        row_tiles = []
        for col in range(1, size + 1):
            key = f"{row_letter}{col}"
            symbol = "✅" if board[key]["complete"] else "❌"
            row_tiles.append(symbol)
        msg += " ".join(row_tiles) + "\n"
    return msg

data = load_data()
bot = commands.Bot(command_prefix="!", intents=config.intents)

@bot.command()
async def complete(ctx, tier, tile):
    team_name = get_team(ctx.author.id)
    tile = tile.upper()

    if not team_name:
        await ctx.send("You are not part of a team.")
        return

    team = data["teams"][team_name]
    boards = team["boards"]

    if tier not in boards or tile not in boards[tier]:
        await ctx.send("Invalid tile or tier.")
        return

    tile_data = boards[tier][tile]
    if tile_data["complete"]:
        await ctx.send("Tile already completed.")
        return

    tile_data["complete"] = True
    team["points"] += data["tile_points"][tier]
    await ctx.send(f"Tile {tile} ({tile_data['name']}) completed for Team {team_name}! Total points: {team['points']}")

    check_unlocks(team_name, ctx)
    save_data()

def check_unlocks(team_name, ctx=None):
    team = data["teams"][team_name]
    for tier, threshold in data["tier_thresholds"].items():
        if tier not in team["unlocked_tiers"] and team["points"] >= threshold:
            team["unlocked_tiers"].append(tier)
            if ctx:
                asyncio.create_task(ctx.send(f"Team {team_name} has unlocked the **{tier}** tier!"))
                board_msg = visualize_board(team["boards"][tier])
                asyncio.create_task(ctx.send(f"__{tier.title()} Board:__\n{board_msg}"))

def get_team(user_id):
    for team, details in data["teams"].items():
        if str(user_id) in details["members"]:
            return team
    return None

@bot.command()
async def team(ctx):
    team_name = get_team(ctx.author.id)
    if not team_name:
        await ctx.send("You are not part of a team.")
        return

    team = data["teams"][team_name]
    msg = f"**Team {team_name} Status**\nPoints: {team['points']}\nUnlocked Tiers: {', '.join(team['unlocked_tiers'])}"
    await ctx.send(msg)

@bot.command()
async def leaderboard(ctx):
    sorted_teams = sorted(data["teams"].items(), key=lambda x: x[1]["points"], reverse=True)
    msg = "**Leaderboard:**\n"
    for i, (team_name, details) in enumerate(sorted_teams, 1):
        msg += f"{i}. Team {team_name} - {details['points']} points\n"
    await ctx.send(msg)

@bot.command()
async def boards(ctx):
    team_name = get_team(ctx.author.id)
    if not team_name:
        await ctx.send("You are not part of a team.")
        return

    team = data["teams"][team_name]
    msg = "**Your Boards:**\n"
    for tier in team["unlocked_tiers"]:
        msg += f"\n__{tier.title()} Board:__\n"
        msg += visualize_board(team["boards"][tier])
    await ctx.send(msg)

@bot.command()
@commands.has_permissions(administrator=True)
async def forceunlock(ctx, team_name, tier):
    if team_name not in data["teams"]:
        await ctx.send("Invalid team.")
        return

    if tier in data["tier_thresholds"] and tier not in data["teams"][team_name]["unlocked_tiers"]:
        data["teams"][team_name]["unlocked_tiers"].append(tier)
        await ctx.send(f"Team {team_name} has been forcefully granted the {tier} tier.")
        save_data()
    else:
        await ctx.send("Invalid tier or tier already unlocked.")

@bot.command()
@commands.has_permissions(administrator=True)
async def status(ctx, *, team_name):
    team_name = team_name.strip()
    if team_name not in data["teams"]:
        await ctx.send("Invalid team.")
        return

    team = data["teams"][team_name]
    msg = f"**Team {team_name} Status**\nPoints: {team['points']}\nUnlocked Tiers: {', '.join(team['unlocked_tiers'])}"
    await ctx.send(msg)

@bot.command()
@commands.has_permissions(administrator=True)
async def adjust(ctx, team_name, points: int):
    if team_name not in data["teams"]:
        await ctx.send("Invalid team.")
        return

    data["teams"][team_name]["points"] += points
    await ctx.send(f"Adjusted Team {team_name}'s points by {points}. New total: {data['teams'][team_name]['points']}")
    check_unlocks(team_name, ctx)
    save_data()

@bot.command()
@commands.has_permissions(administrator=True)
async def complete_easy_medium(ctx, team_name):
    if team_name not in data["teams"]:
        await ctx.send("Invalid team.")
        return

    team = data["teams"][team_name]
    total_points = 0

    for tier in ["easy", "medium"]:
        if tier not in team["boards"]:
            await ctx.send(f"{tier.title()} board not found for Team {team_name}.")
            return

        for tile_data in team["boards"][tier].values():
            if not tile_data["complete"]:
                tile_data["complete"] = True
                total_points += data["tile_points"][tier]

    team["points"] += total_points
    await ctx.send(f"Marked all easy and medium tiles as complete for Team {team_name}. Total points increased by {total_points}.")
    check_unlocks(team_name, ctx)
    save_data()

if __name__ == "__main__":
    bot.run(config.TOKEN)
