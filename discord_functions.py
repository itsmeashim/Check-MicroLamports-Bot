from discord_logger import send_message_to_discord, send_exception_to_discord
import requests
import re
from dotenv import load_dotenv
import logging
import os

load_dotenv()

log_webhook_url = os.getenv("LOG_WEBHOOK_URL")
webhook_url = os.getenv("WEBHOOK_URL")
DC_TOKEN = os.getenv("DC_TOKEN")

def get_response(channel_id):
    data_reversed = []
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    header = {
        'authorization': DC_TOKEN
    }
    response = requests.get(url, headers=header).json()
    # print(response)
    if isinstance(response, list):
        data_reversed = response[::-1]
    # print(f"Response: {data_reversed}")
    return data_reversed

def process_message(message):
    try:
        embeds = message.get('embeds', {})
        embed = embeds[0] if len(embeds) > 0 else ''
        if not embed:
            return "", ""
        message_title = embed.get('title', '')
        message_fields = embed.get('fields', '')
        if not message_fields:
            return "", ""
        print(f"Message title: {message_title}")
        logging.info(f"Message title: {message_title}")

        fields_values = [list(field.values()) for field in message_fields]

        mint_address, mint_amount_supply, mint_amount, supply, minted_by, links, solscan_link = "", "", "", "0", "", "", ""
        for field in fields_values:
            mint_address = next((field['value'].split('](')[0].rstrip(')').strip('[') for field in message_fields if field['name'] == "Mint Address"), None)
            mint_amount_supply = next((field['value'] for field in message_fields if field['name'] == "Mint Amount / Supply"), None)
            
            mint_amount_supply = mint_amount_supply.split('/') if mint_amount_supply else None
            mint_amount = mint_amount_supply[0].strip().split(" ")[0] if mint_amount_supply else 0
            supply = mint_amount_supply[1].strip().split(" ")[0] if mint_amount_supply else 0
            supply = int(round(float(supply))) if supply else 0

            minted_by = next((field['value'].split('](')[0].rstrip(')').strip('[') for field in message_fields if field['name'] == "Minted By"), None)
            links = next((field['value'] for field in message_fields if field['name'] == "Links"), None)

            # regex to find https://solscan.io/tx/* link from the links variable, jsut the first one
            solscan_link = re.search(r'((https://solscan.io/tx/)([\w\d]+))', links).group(3) if links else None

            send_message_to_discord(f"[{mint_address}](https://solscan.io/account/{mint_address}) - [{solscan_link}](https://solscan.io/tx/{solscan_link})", log_webhook_url)

            logging.info(f"ADDRESS: {solscan_link}")

            return solscan_link, embed
            
    except Exception as e:
        print(f"Error: {e}")
        send_exception_to_discord(e, log_webhook_url)
    return "", ""


def send_alert_to_discord(guild_id, channel_id, message_id, embed):
    link = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"

    embed_pd = {
        "title": f"Contract with microlamport 300k found",
        "url": link
    }

    data = {
        "embeds": [embed_pd, embed]
    }
    requests.post(webhook_url, json=data)
