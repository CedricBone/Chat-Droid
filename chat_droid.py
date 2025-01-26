import discord
import requests
import json
import os

# Load the bot token from environment variables
DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"  # Replace with your actual bot token
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Intents for Discord bot
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot client
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Chat Droid is online! Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore the bot's own messages

    if message.content.startswith("!ask"):
        prompt = message.content[len("!ask "):].strip()

        if not prompt:
            await message.channel.send("❌ Please provide a question after `!ask`.")
            return

        await message.channel.send("🤖 Thinking...")

        # Make request to Ollama API
        payload = {
            "model": "deepseek-r1:8b",
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(OLLAMA_API_URL, json=payload)

        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', 'No response from the model.')
            await message.channel.send(f"💬 **Chat Droid:** {generated_text}")
        else:
            await message.channel.send("❌ Error communicating with Ollama.")

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
