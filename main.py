from discord_logger import *
from discord_functions import get_response
from functions import check_response
import time
import random
import logging
import os

logging.basicConfig(level=logging.INFO)

SONIC_ID = os.getenv("SONIC_ID")
guild_id = os.getenv("guild_id")
log_webhook_url = os.getenv("LOG_WEBHOOK_URL")
webhook_url = os.getenv("WEBHOOK_URL")

if __name__ == "__main__":
    i = 0
    sonic_prev_id = 0

    while True:
        # Increment check count and print status
        i += 1
        print(f"Checking Now, times checked: {i}")
        logging.info(f"Checking Now, times checked: {i}")

        try:
            sonic_response = get_response(SONIC_ID)

            for response in sonic_response:
                latest_message_id = sonic_response[-1]['id']
                sonic_new_id = check_response(response, sonic_prev_id, latest_message_id, SONIC_ID, guild_id)
                sonic_prev_id = sonic_new_id if sonic_new_id else sonic_prev_id
        except Exception as e:
            print(f"Error: {e}")
            send_exception_to_discord(e, log_webhook_url)

        if not i == 1:
            # time.sleep(random.uniform(25, 30))
            time.sleep(5)