# 🛡️ Skill Issue - OSRS Combat Achievements Clan Event Bot

**Skill Issue** is a custom Discord bot designed to manage OSRS Combat Achievement clan events. It tracks team progress, points, and unlocks as players work through bingo-style Combat Achievement boards.

---

## ⚙️ Features

✅ Supports dynamic board sizes (2x2, 3x3, 4x4, etc.)

✅ Tracks tile completion and automatically awards points

✅ Automatically unlocks higher-tier boards based on points thresholds

✅ Team-based leaderboard

✅ Admin commands for manual adjustments, unlocking, and event control

---

## 📦 Requirements

- Python 3.8+
- `discord.py`
- Your bot's Discord token and configured intents (see `config.py`, `.env`)
- `skill_issue_data.json` file to store event state

---

## 🚀 Setup

1. Clone this project
2. Create a `config.py` file:

```python
from dotenv import load_dotenv # type: ignore
import os
import discord # type: ignore

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
intents.message_content = True
```

and a `.env`:

`DISCORD_TOKEN="discord_token_here"`

3. Run the bot:

```bash
python bot.py
```

---

## 📝 Core Commands

| Command                   | Description                                     | Access  |
| ------------------------- | ----------------------------------------------- | ------- |
| `!complete <tier> <tile>` | Mark a tile complete (e.g. `!complete easy A1`) | Players |
| `!team`                   | View your team's points & unlocked tiers        | Players |
| `!leaderboard`            | Show team rankings by points                    | Players |
| `!boards`                 | View your team's boards                         | Players |

---

## 🛠️ Admin Commands

| Command                             | Description                                                           |
| ----------------------------------- | --------------------------------------------------------------------- |
| `!forceunlock <team_name> <tier>`   | Manually unlock a board for a team                                    |
| `!status <team_name>`               | View detailed status for a specific team                              |
| `!adjust <team_name> <points>`      | Add/subtract points from a team                                       |
| `!complete_easy_medium <team_name>` | Automatically completes easy & medium boards, awarding correct points |

---

## 🗂 Data Structure

- All event data is stored in `skill_issue_data.json`
- Includes teams, member IDs, boards, tile states, and points

---

## 💾 Backups

Every time data is saved, a backup is written to `backup_skill_issue_data.json`.

---

## 🧹 Reset Script (Optional)

If desired, run `python reset_teams.py` to wipe all completions and reset points.

---

## 🏁 Notes

- Only players with registered Discord IDs in a team can use player commands.
- Admin commands require Discord admin permissions. Could change this to roles=refs.
- Boards can be hand-built in the JSON file to any square size.
