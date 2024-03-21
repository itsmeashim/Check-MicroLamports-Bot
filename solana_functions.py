import requests
import time
import random
import json
from discord_functions import send_exception_to_discord, log_webhook_url, send_message_to_discord
import os
from dotenv import load_dotenv

load_dotenv()

log_webhook_url = os.getenv("LOG_WEBHOOK_URL")
webhook_url = os.getenv("WEBHOOK_URL")
API_URL = os.getenv("API_URL")

# Define the API endpoint and payload
url = API_URL

def get_transaction(hash: str):
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                hash,
                {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}
            ]
        }
        response = requests.post(url, json=payload)
        # print(response.text)
        return response.text
    except Exception as e:
        print(f"Error: {e}")
        send_exception_to_discord(e, log_webhook_url)
        return json.dumps({"error": f"Error: {e}"})

def validMicroLamports(hash: str):
    # try:
    i = 1
    while True:
        if i > 5:
            send_message_to_discord(f"**Transaction not confirmed, tried 5 times, exiting...**", log_webhook_url, 0xff4c4c)
            return False
        transaction_response = json.loads(get_transaction(hash))
        if transaction_response['result'] == None:
            send_message_to_discord(f"**Try: {i}. Transaction not confirmed, retrying in 7 seconds...**", log_webhook_url, 0x36135a)
            i += 1
            time.sleep(7)
            continue
        else:
            break

    if 'error' in transaction_response:
        return False

    if 'error' in transaction_response:
        return False

    instructions = transaction_response.get("result", {}).get("transaction", {}).get("message", {}).get("instructions", [])

    if not instructions:
        send_message_to_discord(f"**Transaction Confirmed. No instructions found.**", log_webhook_url, 0xffa5a5)
        return False

    for instruction in instructions:
        print(instruction)
        programId = instruction.get("programId")
        if not programId == "ComputeBudget111111111111111111111111111111":
            continue

        data = instruction.get("data")

        print(programId, data)

        if not data:
            send_message_to_discord(f"**Transaction Confirmed. No data found.**", log_webhook_url, 0xffa5a5)
            return False

        if data == "3s2DQSEX3t4P":
            send_message_to_discord(f"**Transaction Confirmed. Data found.**", log_webhook_url, 0x5cd65c)
            return True

        send_message_to_discord(f"**Transaction Confirmed. Data found but not valid. {data}**", log_webhook_url, 0xffa5a5)

    # except Exception as e:
    #     print(f"Error: {e}")
    #     send_exception_to_discord(e, log_webhook_url)
    return False
