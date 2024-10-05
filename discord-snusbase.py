import discord
from discord.ext import commands
import requests
import base64
import tempfile
import os
from flask import Flask
import threading

# Flask server setup
app = Flask(__name__)

@app.route('/')
def index():
    return "Flask server is running on 0.0.0.0!"

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True  # Make sure this is enabled
bot = commands.Bot(command_prefix='!', intents=intents)

SEARCH_TYPES = ["email", "username", "name", "password", "hash", "lastip"]

async def search(search_input, search_type):
    """Executes the search via the API and returns the results"""
    key = 'c2J5anRoa29mdDR5YWltYndjanFwbXhzOGh1b3Zk'
    mensaje_base64_bytes = key.encode('utf-8')
    mensaje_decodificado_bytes = base64.b64decode(mensaje_base64_bytes)
    apiKey = mensaje_decodificado_bytes.decode('utf-8')

    url = 'https://api-experimental.snusbase.com/data/search'
    headers = {
        'Auth': apiKey,
        'Content-Type': 'application/json'
    }
    payload = {
        'terms': [search_input],
        'types': [search_type],
        'wildcard': False
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get('results', {})
        else:
            print(f"Error: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Connection error: {e}")
        return None

async def save_results_to_tempfile(results):
    """Saves the results to a temporary .txt file"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
        for database, entries in results.items():
            temp_file.write(f"Database: {database}\n".encode())
            temp_file.write(b"-" * 50 + b"\n")
            for entry in entries:
                for key, value in entry.items():
                    temp_file.write(f"[+] {key}: {value}\n".encode())
                temp_file.write(b"-" * 50 + b"\n")
        return temp_file.name

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

@bot.command(name='search-snusbase', help='Search for a specific term with a given type (email, password, hash)')
async def search_command(ctx, search_type: str, *, search_input: str):
    """Command to search for a specific term with a given type"""
    search_type = search_type.lower()
    if search_type in SEARCH_TYPES:
        results = await search(search_input, search_type)
        if results:
            temp_file_path = await save_results_to_tempfile(results)
            # Send the file in DM to the user
            await ctx.author.send("Here are your search results:", file=discord.File(temp_file_path))
            # Remove the temporary file after sending
            os.remove(temp_file_path)
            await ctx.send("The results have been sent in DM.")
        else:
            await ctx.send("No results found or search error.")
    else:
        await ctx.send("Invalid search type. Use: " + ", ".join(SEARCH_TYPES))

@bot.command(name='help-snusbase', help='Get help on using the Snusbase search commands')
async def help_command(ctx):
    """Help command to provide users with usage instructions"""
    help_text = (
        "**Snusbase Help**\n"
        "Use the `!search-snusbase` command to look up information.\n"
        "Available search types:\n"
        f"- {', '.join(SEARCH_TYPES)}\n"
        "Example usage: `!search email example@example.com`\n"
        "This command will search for the provided email."
    )
    await ctx.send(help_text)

# Function to run the bot
def run_discord_bot():
    # Base64 encoded bot token
    base64_token = 'TVRJOE1qTXdNVEE3T0RJeU56WTlMT0cuQ2luV1NzLjkzQ2FwVXZyWVE5WTlIRUNQQWxnWGlHVDY3OEFla1p6Q00' 
    # Decoding the token
    decoded_token = base64.b64decode(base64_token).decode('utf-8')
    bot.run(decoded_token)

# Run both Flask server and Discord bot
if __name__ == "__main__":
    # Run Flask in a separate thread
    threading.Thread(target=run_flask).start()

    # Run the bot
    run_discord_bot()
