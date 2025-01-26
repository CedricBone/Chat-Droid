import discord
import requests
import os
import re
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

# Allowed models 
ALLOWED_MODELS = ["r1-14b", "some-other-model"]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# In-memory conversation history:
# Key: user_id (int)
# Value: list of tuples (("user", user_message), ("assistant", assistant_response))
conversation_history = {}


def build_conversational_prompt(history_tuples, new_user_prompt):
    """
    Given a list of (role, text) tuples, build a single conversation prompt string.
    We'll represent the conversation in a simple format:
       "User: ...\nAssistant: ...\nUser: ...\nAssistant: ...\nUser: <new_user_prompt>\nAssistant:"
    """
    prompt_lines = ["Below is a conversation between a user and an assistant."]
    for role, text in history_tuples:
        if role == "user":
            prompt_lines.append(f"User: {text}")
        else:  # role == "assistant"
            prompt_lines.append(f"Assistant: {text}")

    # Add the new user message
    prompt_lines.append(f"User: {new_user_prompt}")
    prompt_lines.append("Assistant:")
    return "\n".join(prompt_lines)


def query_ollama(prompt, model="r1-14b", temperature=0.7):
    """
    Query Ollama with the given prompt, model, and temperature.
    Uses a try/except block for error handling.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get('response', 'No response from model.')
        else:
            return f"Error: Ollama returned status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        # This will catch connection errors, timeouts, etc.
        return f"Error: Could not communicate with Ollama. Details: {str(e)}"


def parse_r1_output(raw_text, show_thinking=False):
    """
    For 'reasoning' models (like r1-14b), optionally remove:
      - '>>> ...' lines
      - <think>...</think> blocks (if show_thinking=False)
    """
    # Remove lines starting with ">>>"
    lines = []
    for line in raw_text.splitlines():
        if line.strip().startswith(">>>"):
            continue
        lines.append(line)
    text_without_arrows = "\n".join(lines)

    # If show_thinking is False, strip out <think>...</think> blocks
    if not show_thinking:
        text_without_arrows = re.sub(r'<think>.*?</think>', '', text_without_arrows, flags=re.DOTALL)

    return text_without_arrows


@bot.event
async def on_ready():
    print(f"✅ Chat Droid is online! Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")


# Slash command: /ask
@bot.tree.command(name="ask", description="Ask the LLM a question")
@app_commands.describe(
    prompt="The prompt or question to ask the LLM",
    model="(Optional) Model to use; defaults to r1-14b",
    temperature="(Optional) Creativity level 0.0-1.0; defaults to 0.7",
    show_thinking="(Optional) True/False. If True, shows <think> blocks in r1 outputs",
    preserve_history="(Optional) True/False. If True, the conversation context is remembered"
)
async def ask_command(
    interaction: discord.Interaction,
    prompt: str,
    model: str = "r1-14b",
    temperature: float = 0.7,
    show_thinking: bool = False,
    preserve_history: bool = False
):
    """
    Examples:
      /ask prompt:"Hello!"
      /ask prompt:"Explain quantum mechanics" model:"r1-14b" temperature:0.5 show_thinking:true
      /ask prompt:"Let's continue" preserve_history:true
    """
    await interaction.response.defer()

    warnings = []

    # Validate model
    if model not in ALLOWED_MODELS:
        warnings.append(f"Unsupported model '{model}', using 'r1-14b' instead.")
        model = "r1-14b"

    # Validate temperature
    if temperature < 0.0 or temperature > 1.0:
        warnings.append(f"Temperature {temperature} is out of [0.0, 1.0], using 0.7 instead.")
        temperature = 0.7

    user_id = interaction.user.id

    if preserve_history:
        # Build prompt from conversation history + new user prompt
        user_history = conversation_history.get(user_id, [])
        full_prompt = build_conversational_prompt(user_history, prompt)
    else:
        # Single call, ignoring any stored context
        full_prompt = prompt

    # Query Ollama
    response = query_ollama(full_prompt, model=model, temperature=temperature)

    # If it's an r1-type model, optionally remove <think> blocks
    if model.startswith("r1"):
        response = parse_r1_output(response, show_thinking=show_thinking)

    # If preserving conversation, store user + assistant messages
    # (store the final displayed text so we don't re-insert <think> blocks)
    if preserve_history and not response.startswith("Error:"):
        # If new conversation, create an empty list
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        # Append the new user message + the assistant response
        conversation_history[user_id].append(("user", prompt))
        conversation_history[user_id].append(("assistant", response))

    # Prepend any warnings to the response
    if warnings:
        response = "\n".join(warnings) + "\n\n" + response

    await interaction.followup.send(f"💬 **Chat Droid:** {response}")


# Slash command: /clearcontext
@bot.tree.command(name="clearcontext", description="Clear your conversation history with the bot")
async def clearcontext_command(interaction: discord.Interaction):
    """
    Clears the stored conversation context for the user.
    """
    user_id = interaction.user.id
    if user_id in conversation_history:
        del conversation_history[user_id]
        await interaction.response.send_message("Your conversation history has been cleared.")
    else:
        await interaction.response.send_message("No conversation history found to clear.")


# Slash command: /help
@bot.tree.command(name="help", description="Show usage instructions for Chat Droid")
async def help_command(interaction: discord.Interaction):
    """
    Provides a quick guide on how to use Chat Droid's slash commands.
    """
    help_text = (
        "**Welcome to Chat Droid!**\n\n"
        "Use the `/ask` command to query the LLM.\n\n"
        "**/ask parameters**:\n"
        "• **prompt** (required): The text or question you want answered.\n"
        "• **model** (optional): Defaults to `r1-14b`. Allowed: [r1-14b, some-other-model].\n"
        "• **temperature** (optional): Float in [0.0,1.0], default 0.7.\n"
        "• **show_thinking** (optional, bool): If True, keeps <think> blocks for r1 outputs.\n"
        "• **preserve_history** (optional, bool): If True, the bot remembers prior messages.\n\n"
        "**Example usage**:\n"
        "`/ask prompt:\"What is the capital of France?\"`\n"
        "`/ask prompt:\"Explain quantum physics\" model:\"r1-14b\" temperature:0.5 show_thinking:true`\n"
        "`/ask prompt:\"Let's continue that topic\" preserve_history:true`\n\n"
        "**Clearing Context**:\n"
        "Use `/clearcontext` to erase your conversation history.\n\n"
        "If you encounter any issues, please contact the admin!"
    )
    await interaction.response.send_message(help_text)


# Run the bot
bot.run(DISCORD_BOT_TOKEN)
