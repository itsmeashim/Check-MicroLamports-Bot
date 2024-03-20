from discord_logger import send_message_to_discord, send_exception_to_discord
from solana_functions import validMicroLamports
from discord_functions import send_alert_to_discord, process_message
from dotenv import load_dotenv
import os

load_dotenv()

log_webhook_url = os.getenv("LOG_WEBHOOK_URL")
webhook_url = os.getenv("WEBHOOK_URL")

def check_response(response, prev_id, latest_message_id, channel_id, guild_id):
    try:
        latest_message = response
        prev_id = latest_message_id if not prev_id else prev_id
        new_id = int(latest_message['id'])

        if int(prev_id) < int(new_id):
            contract_address, embed = process_message(latest_message)
            print(f"Contract Address: {contract_address}")

            isValid = validMicroLamports(contract_address) if contract_address else False
            if isValid:
                send_alert_to_discord(guild_id, channel_id, new_id, embed)
                send_message_to_discord(f"Transaction with lamports 300k found", log_webhook_url, 0x287e29)

            return new_id
    except Exception as e:
        print(f"Error: {e}")
        send_exception_to_discord(e, log_webhook_url)
    return prev_id

