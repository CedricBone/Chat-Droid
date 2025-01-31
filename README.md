# Chat Droid

A Discord bot powered by [Ollama](https://github.com/jmorganca/ollama).  
It forwards your prompts to Ollama's endpoint and posts the responses in a Discord channel.  
Now supports **optional conversation memory** per user (toggle with `/ask preserve_history:true`), with a `/clearcontext` command to reset.

---

## Features

1. **Slash Command**: `/ask`
   - **prompt** (required): The text or question you want to ask.
   - **model** (optional): Defaults to `r1-14b`. (Allowed models: `"r1-14b"`, `"some-other-model"`.)
   - **temperature** (optional): Float in `[0.0, 1.0]`; defaults to `0.7`.
   - **show_thinking** (optional, bool): If `True` and using `r1-14b`, displays `<think>...</think>` blocks.
   - **preserve_history** (optional, bool): If `True`, the bot remembers previous user/bot messages (per user).

2. **Context Clearing**: `/clearcontext`
   - Erases conversation memory for **your** user ID.

3. **Error Handling**:
   - Shows friendly messages if Ollama is unreachable or other issues arise.

4. **Model & Temperature Validation**:
   - If an invalid model or out-of-range temperature is given, the bot falls back to defaults and warns.

5. **Help Command**: `/help`
   - Explains usage and parameters, including how to enable/clear conversation memory.

---

## Requirements

1. **Python 3.9+** (Recommended)
2. **Dependencies**:
    - `discord.py`
    - `requests`
    - `python-dotenv`
3. **Ollama**:
   - Install and run [Ollama](https://github.com/jmorganca/ollama) to handle text generation requests.
4. **Discord Bot Token**:
   - Create a bot in the [Discord Developer Portal](https://discord.com/developers).
   - Enable the `applications.commands` scope for slash commands.
5. **Network Access**:
   - The bot must reach the Ollama server endpoint (by default `http://localhost:11411/completion`).

---

## Installation and Setup

1. **Clone or Download** this codebase.

2. **Create a `.env` File** in the project’s root folder, containing at least:
   ```dotenv
   DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN
   OLLAMA_API_URL=http://localhost:11411/completion
