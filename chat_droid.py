import discord
import requests
import os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

# Set up the bot with command tree for slash commands
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to query Ollama
def query_ollama(prompt, model="deepseek-r1:8b", temperature=0.7):
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code == 200:
        return response.json().get('response', 'No response from model.')
    return "Error: Could not communicate with Ollama."

@bot.event
async def on_ready():
    print(f"✅ Chat Droid is online! Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# Slash command to ask the LLM a question
@bot.tree.command(name="ask", description="Ask the LLM a question")
@app_commands.describe(question="What would you like to ask?")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    response = query_ollama(question)
    await interaction.followup.send(f"💬 **Chat Droid:** {response}")

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
