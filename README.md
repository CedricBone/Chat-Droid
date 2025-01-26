# Chat Droid

A Discord bot powered by [Ollama](https://github.com/jmorganca/ollama).  
It sends your prompt to Ollama's endpoint and returns the response in a Discord channel.  
Now supports **optional conversation memory** per user (toggleable via `/ask preserve_history:true`), with a `/clearcontext` command to reset.

---

## Features

1. **Slash Command**: `/ask`
   - **prompt** (required): Your question or text to prompt the model.
   - **model** (optional): Defaults to `r1-14b`. Allowed values: `["r1-14b", "some-other-model"]`.
   - **temperature** (optional): Float in `[0.0, 1.0]`, defaults to 0.7.
   - **show_thinking** (optional, bool): By default `False`. If `True`, shows `<think>...</think>` blocks in `r1-14b` model responses.
   - **preserve_history** (optional, bool): If `True`, the bot remembers your conversation context (per user).  
     - You can continue a topic across multiple `/ask` commands without losing context.

2. **Clearing Conversation**: `/clearcontext`  
   - Erases all stored conversation history for **your** user ID.

3. **Error Handling**:
   - Returns friendly error messages if Ollama is unreachable or other issues occur.

4. **Model & Temperature Validation**:
   - Falls back to defaults if invalid values are provided.

5. **Help Command**: `/help`  
   - Shows usage details, including how to set `preserve_history`.

---

## Requirements

1. **Python 3.9+** (Recommended)
2. **Dependencies**:
    - `discord.py`
    - `requests`
    - `python-dotenv`
3. **Ollama**:
   - Install and run [Ollama](https://github.com/jmorganca/ollama) in the background.
4. **Discord Bot Token**:
   - Create a bot in the [Discord Developer Portal](https://discord.com/developers).
   - Enable `applications.commands` scope for slash commands.

---

## Installation

### 1. Download or Clone the Code

```bash
git clone https://github.com/your-repo/chat-droid.git
cd chat-droid
