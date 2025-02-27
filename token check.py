#check if bot token is valid (to be added to easy-compiler.py later)

import requests

def is_valid_discord_token(token):
    url = "https://discord.com/api/v10/users/@me"
    headers = {"Authorization": f"Bot {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Valid bot token!")
        return True
    elif response.status_code == 401:
        print("Invalid bot token!")
        return False
    else:
        print(f"Unexpected response ({response.status_code}): {response.text}")
        return None  # Could be a rate limit or other error

# Example usage
bot_token = "bot token or random string"
is_valid_discord_token(bot_token)
