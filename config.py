from dotenv import load_dotenv # type: ignore
import os
import discord # type: ignore

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
intents.message_content = True
